import time
import boto3
import os

s3 = boto3.resource('s3')
for file in os.listdir('input_audios'):
    s3.meta.client.upload_file('input_audios/' + file, 'sample-conversation-file-bucket', file)

s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')

response = s3_client.list_objects('sample-conversation-file-bucket')
for content in response['Contents']:
    transcribe_client.start_transcription_job(
        TranscriptionJobName=content['Key'],
        LanguageCode='en-US',
        MediaFormat='wav',
        Media={
            'MediaFileUri': 's3' + 'sample-conversation-file-bucket' + content['Key']
        },
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=content['Key'])
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status == 'COMPLETED':
            text_file_s3_uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
            break
        else:
            time.sleep(10)

    print(text_file_s3_uri)
