# pdf2image-lambda
Create images from PDF documents uploaded to S3 buckets.  
The images are placed next to the original file with numbered suffixes.  

Thanks to Lambda's concurrency, this approach is well-suited to variable bulk/batch higher-volume conversion workloads.  
Please double check you are in the AWS region you intend; this needs to be the **same region** as the bucket which will contain the PDF documents you wish to convert.  

## Execution Role
Ensure that your execution role has both "s3:GetObject" and "s3:PutObject" permissions on the source buckets.  
Without GetObject/PutObject permission on the triggering bucket you'll get Access Denied errors.

## S3 Trigger
This function responds to S3 ObjectCreated events.  

To configure the trigger, on the Lambda function, in "Designer > Add triggers", click "S3". The "Configure triggers" dialog appears.
Select a bucket (any time a pdf is added to this bucket, the function will run).  
Verify that "all object create events" is selected (or choose PUT POST or COPY).  
Click "Add" (bottom right), then "Save" (top right).

## Confirm successful installation
### S3 Trigger
If you configured the S3 trigger, you can try it, by copying a PDF document into the S3 bucket you have set the trigger on.  
To verify it works, look for a PDF in your output bucket, or check the logs in cloudwatch

### Sizing Notes
If you observe "Process exited before completing request" errors, it might point to your lambda function not having sufficient access to sufficient resources, or having insufficient time-out period.

##### Memory
Experience suggests assigning *2048MB*.  
This can be set under the "Memory (MB)" header in the "Basic settings" section of the Lambda function configuration tab.

##### Timeout
The time taken for the Lambda to run, will depend on the size of the PDF document being processed.  
For maximum flexibility, allow a 15 minute timeout, although experience suggests that the function should hardly ever take longer than a few seconds to run.  

This can be set under the "Timeout" header in the "Basic settings" section of the Lambda function configuration tab.
