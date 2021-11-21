import time
import boto3
import os
import json
import urllib.request as urllib2

s3 = boto3.resource('s3')
for file in os.listdir('input_audios'):
    s3.meta.client.upload_file('input_audios/' + file, 'sample-conversation-file-bucket', file)

s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')

response = s3_client.list_objects(
    Bucket='sample-conversation-file-bucket'
)
for content in response['Contents']:
    print(content['Key'])
    try:
        transcribe_client.start_transcription_job(
            TranscriptionJobName=content['Key'],
            LanguageCode='en-US',
            MediaFormat='wav',
            Media={
                'MediaFileUri': 's3://' + 'sample-conversation-file-bucket/' + content['Key']
            },
        )
    except:
        print('already exist')

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

    response = urllib2.urlopen(text_file_s3_uri)
    data_json = json.loads(response.read())

    file_name = 'output_text_files/' + content['Key']
    text_file = open(file_name[:-3] + 'txt', "w")
    text_file.write(data_json['results']['transcripts'][0]['transcript'])
    text_file.close()
