import time
import boto3
import os


def transcribe_file(job_name, file_uri, transcribe_client):
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='wav',
        LanguageCode='en-US'
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            print(f"Job {job_name} is {job_status}.")
            if job_status == 'COMPLETED':
                print(
                    f"Download the transcript from\n"
                    f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}.")
            break
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)


def upload_to_s3():
    s3 = boto3.resource('s3')
    for file in os.listdir('input_audios'):
        s3.meta.client.upload_file('input_audios/' + file, 'sample-conversation-file-bucket', file)


def main():
    upload_to_s3()
    s3_client = boto3.client('s3')
    transcribe_client = boto3.client('transcribe')
    response = s3_client.list_objects('sample-conversation-file-bucket')
    for content in response['Contents']:
        transcribe_client.start_transcription_job(
            TranscriptionJobName='',
            Media='',
            
        )
        content['Key']
    transcribe_client = boto3.client('transcribe')
    file_uri = 's3://sample-conversation-file-bucket/11-18-2021_12-11-26_sid_48468966_dbsid_823.wav'
    transcribe_file('Example-job', file_uri, transcribe_client)


if __name__ == '__main__':
    main()
