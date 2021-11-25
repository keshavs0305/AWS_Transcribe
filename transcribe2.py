import time
import boto3
import os
import json
import urllib.request as urllib2
from datetime import datetime
import pandas as pd

# s3 = boto3.resource('s3')
# for file in os.listdir('input_audios'):
#    s3.meta.client.upload_file('input_audios/' + file, 'sample-conversation-file-bucket', file)

s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')

response = s3_client.list_objects(
    Bucket='sample-conversation-file-bucket'
)

for content in response['Contents']:
    try:
        now = datetime.now()
        transcribe_client.start_transcription_job(
            TranscriptionJobName='11-18-2021_12-07-38_sid_48468986_dbsid_823.wav231121021130',
            # TranscriptionJobName=content['Key']+now.strftime("%d%m%y%H%m%S"),
            LanguageCode='en-US',
            MediaFormat='wav',
            Media={
                'MediaFileUri': 's3://' + 'sample-conversation-file-bucket/' + content['Key']
            },
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 2
            }
        )
    except Exception as e:
        print(e)

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(
            TranscriptionJobName='11-18-2021_12-07-38_sid_48468986_dbsid_823.wav231121021130')
        # job = transcribe_client.get_transcription_job(TranscriptionJobName=content['Key']+now.strftime("%d%m%y%H%m%S"))
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status == 'COMPLETED':
            text_file_s3_uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
            break
        else:
            time.sleep(10)

    response = urllib2.urlopen(text_file_s3_uri)
    data_json = json.loads(response.read())

    seg_start = []
    seg_end = []
    seg_spk = []
    for seg in data_json['results']['speaker_labels']['segments']:
        for item in seg['items']:
            seg_start.append(item['start_time'])
            seg_end.append(item['end_time'])
            seg_spk.append(item['speaker_label'])
    item_start = []
    item_end = []
    item_text = []

    for item in data_json['results']['items']:
        try:
            item_start.append(item['start_time'])
            item_end.append(item['end_time'])
            item_text.append(item['alternatives'][0]['content'])
        except:
            item_text[-1] += item['alternatives'][0]['content']

    data1 = pd.DataFrame({'start_time': seg_start, 'end_time': seg_end, 'speaker': seg_spk})
    data2 = pd.DataFrame({'start_time': item_start, 'end_time': item_end, 'text': item_text})

    data1.to_csv('data1.csv')
    data2.to_csv('data2.csv')

    # s3_client.delete_object(
    #    Bucket='sample-conversation-file-bucket',
    #
    # )
