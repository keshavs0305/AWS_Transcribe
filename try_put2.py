import boto3
import os

s3 = boto3.resource('s3')

for file in os.listdir('input_audios'):
    s3.meta.client.upload_file('input_audios/'+file, 'sample-conversation-file-bucket', file)
