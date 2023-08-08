import boto3
import logging
from io import BytesIO
from pdf2image import convert_from_bytes

DPI = 300
FMT = "png" # ppm, jpeg, png, tiff
_SUPPORTED_FILE_EXTENSION = '.pdf'

def pdf_to_image(event, context):
    """Take a pdf from an S3 bucket and convert it to a list of pillow images (one for each page of the pdf).
    :param event: A Lambda event (referring to an S3 event object created event).
    :param context: Lambda context object.
    :return:
    """
    if not event.key.endswith(_SUPPORTED_FILE_EXTENSION):
        raise Exception(f"Only .pdf files are supported by this module.")

    logging.info(f"Fetching item (bucket: '{event.bucket}', key: '{event.key}') from S3.")

    # Fetch the image bytes
    s3 = boto3.resource('s3')
    obj = s3.Object(event.bucket, event.key)
    infile = obj.get()['Body'].read()
    logging.info("Successfully retrieved S3 object.")

    # Set poppler path
    poppler_path = "/var/task/lib/poppler-utils-0.26/usr/bin"
    images = convert_from_bytes(infile, dpi=DPI, fmt=FMT, poppler_path=poppler_path)
    logging.info("Successfully converted pdf to image.")

    base_filename = event.key.rsplit('.', 1)[0]
    for page_num, image in enumerate(images):
        location = f"{base_filename}-new-{page_num+1}.{FMT}"
        logging.info(f"Saving page number {str(page_num)} to S3 at location: {event.bucket}, {location}.")

        buffer = BytesIO()
        image.save(buffer, FMT.upper())
        buffer.seek(0)
        s3.Object(event.bucket, location).put(Body=buffer)

    return f"PDF document ({event.key}) successfully converted to a series of images."