import boto3
import logging
import os
from io import BytesIO
from pdf2image import convert_from_bytes

os.environ["LD_LIBRARY_PATH"] = "/var/task/vendor/lib:" + os.environ.get("LD_LIBRARY_PATH", "")

DPI = 300
FMT = "png" # ppm, jpeg, png, tiff
_SUPPORTED_FILE_EXTENSION = '.pdf'
MIME_TYPES = {
    'png': 'image/png',
    'jpeg': 'image/jpeg',
    'tiff': 'image/tiff',
    'ppm': 'image/x-portable-pixmap'
}

def pdf_to_image(event, context):
    """Take a pdf from an S3 bucket and convert it to a list of pillow images (one for each page of the pdf).
    :param event: A Lambda event (referring to an S3 event object created event).
    :param context: Lambda context object.
    :return:
    """

    s3_record = event['Records'][0]['s3']
    bucket_name = s3_record['bucket']['name']
    object_key = s3_record['object']['key']

    if not object_key.endswith(_SUPPORTED_FILE_EXTENSION):
        raise Exception(f"Only .pdf files are supported by this module.")

    logging.info(f"Fetching item (bucket: '{bucket_name}', key: '{object_key}') from S3.")

    # Fetch the image bytes
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name, object_key)
    infile = obj.get()['Body'].read()
    logging.info("Successfully retrieved S3 object.")

    # Set poppler path
    poppler_path = "/var/task/vendor/lib/poppler-utils-0.26/usr/bin"
    images = convert_from_bytes(infile, dpi=DPI, fmt=FMT, poppler_path=poppler_path)
    logging.info("Successfully converted pdf to image.")

    base_filename = object_key.rsplit('.', 1)[0]
    for page_num, image in enumerate(images):
        location = f"{base_filename}-{page_num+1}.{FMT}"
        logging.info(f"Saving page number {str(page_num)} to S3 at location: {bucket_name}, {location}.")

        buffer = BytesIO()
        image.save(buffer, FMT.upper())
        buffer.seek(0)

        mime_type = MIME_TYPES.get(FMT, 'application/octet-stream')
        s3.Object(bucket_name, location).put(Body=buffer, ContentType=mime_type)

    return f"PDF document ({object_key}) successfully converted to a series of images."
