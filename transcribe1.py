import time
import boto3
import os
import json
import urllib.request as urllib2
from datetime import datetime

#s3 = boto3.resource('s3')
#for file in os.listdir('input_audios'):
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
            #TranscriptionJobName=content['Key']+now.strftime("%d%m%y%H%m%S"),
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
        job = transcribe_client.get_transcription_job(TranscriptionJobName='11-18-2021_12-07-38_sid_48468986_dbsid_823.wav231121021130')
        #job = transcribe_client.get_transcription_job(TranscriptionJobName=content['Key']+now.strftime("%d%m%y%H%m%S"))
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status == 'COMPLETED':
            text_file_s3_uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
            break
        else:
            time.sleep(10)

    response = urllib2.urlopen(text_file_s3_uri)
    data_json = json.loads(response.read())

    audio_transcribe_job = []
    time_start = []
    speaker = []
    speaker_text = []
    cont_c = 0
    for cont in data_json['results']['speaker_labels']['segments']:
        #audio_transcribe_job.append(content['Key']+now.strftime("%d%m%y%H%m%S"))
        time_start.append(cont['start_time'])
        speaker.append(cont['speaker_label'])
        text = ''
        i = 0
        text = [i['alternatives'][0]['content'] for i in data_json['results']['items']]
        while i < len(cont['items']) and cont_c < len(data_json['results']['items']):
            print(i, len(cont['items']))
            #if (i == len(cont['items'])) and (cont_c < len(data_json['results']['items'])):
            #    print('a')
            #    if data_json['results']['items'][cont_c]['alternatives'][0]['content'] in ['.', '?']:
            #        print('b')
            #        text += data_json['results']['items'][cont_c]['alternatives'][0]['content']
             #   else:
             #       break
            try:
                if i < len(cont['items']):
                    data_json['results']['items'][cont_c]["start_time"]
                    text += data_json['results']['items'][cont_c]['alternatives'][0]['content']
                    text += ' '
                    i += 1
            except:
                text = text[:-1]
                text += data_json['results']['items'][cont_c]['alternatives'][0]['content']
                text += ' '
            print(i, len(cont['items']), text)
            cont_c += 1

        print(cont_c < len(data_json['results']['items']))
        print(data_json['results']['items'][cont_c]['alternatives'][0]['content'] in ['.', '?'])
        if (cont_c < len(data_json['results']['items'])) and (data_json['results']['items'][cont_c]['alternatives'][0]['content'] in ['.', '?']):
            print(text)
            try:
                if speaker_text[-1][-1] == ' ':
                    speaker_text[-1] = speaker_text[-1][:-1]
            except:
                print()
            text += data_json['results']['items'][cont_c]['alternatives'][0]['content']
            print(text)
            #cont_c += 1
        speaker_text.append(text)
        try:
            if speaker_text[-1][-1] == ' ':
                speaker_text[-1] = speaker_text[-1][:-1]
                print(speaker_text[-1])
        except:
            print()
        print(speaker_text)
    print(len(time_start))
    print(len(speaker))
    print(len(speaker_text))
    #print(len(audio_transcribe_job))
    print(speaker_text)

    #s3_client.delete_object(
    #    Bucket='sample-conversation-file-bucket',
    #
    #)
