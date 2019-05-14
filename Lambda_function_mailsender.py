import json
import urllib.parse
import boto3

print('Loading function')

s3 = boto3.client('s3')
sns = boto3.client('sns')

expiration = 25200 #7일 뒤 만료

def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print("Bucket:" + bucket)
    print("Key:" + key)
    try:
        presigned_url = s3.generate_presigned_url(
            'get_object',
             Params = {'Bucket': bucket, 'Key': key},
             ExpiresIn=expiration
        )

        print("Presigned URL to share an S3 object:" + presigned_url)

        emailMessage = '현재 운영 중인 AWS 리소스 비용 효율화 필요. 다운로드 주소(전체 URL 복사 후 브라우저 주소창에 붙여넣어야 함) : ' + presigned_url

        response = sns.publish(
            TopicArn='arn:aws:sns:ap-northeast-2:xxx', #실제 SNS Topic의 Arn을 넣어줄 것
            Message=emailMessage,
        )
        return response
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
