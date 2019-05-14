# cost-management-automation
AWS Cost Management Process를 자동화하기 위해 OpsNow 도구 내 비용 효율화 대상 파일을 자동으로 다운로드해서 담당자가 비용 검토할 수 있도록 자동으로 이메일을 보내기 위한 프로그램이다.

# Configuration
### 1) Webpage Automation 관련 Library를 위한 AWS Lambda Layer 생성
  - Python Folder 아래 파일들을 Python.zip으로 압축 후 Layer에 Upload

### 2) OpsNow 로그인, 비용관리 페이지 내 대상파일 다운로드 및 S3 업로드를 위한 Lambda Function 생성
  - 1)단계에서 생성한 Layer를 추가함
  - Runtime : Python 3.6, 
    Memmory : 512MB, 
    Timeout : 3 min, 
    Execurion role : Lambda basic role에 AmazonS3FullAccess(혹은 업로드 대상 Bucket에 업로드 가능) role 추가
  - Fuction code에 Lambda_function_crawler.py 내 code 추가
  - Configure test event : 
```
  {
    "id": "OpsNow로그인ID",
    "pwd": "OpsNow로그인Password",
    "bucket": "다운로드파일 업로드할 BucketName"
  }
```

### 3) 2)단계 Lambda의 Trigger를 위한 CloudWatch Event 생성
  - CloudWatch Events > Rule > Create rule
  - Schedule 통해 비용관리 자동화 실행할 주기 설정
  - Targets으로 2)단계 Lambda function 지정
    Configure input에 Constant 설정 후 아래 JSON 입력
```
  {
    "id": "OpsNow로그인ID",
    "pwd": "OpsNow로그인Password",
    "bucket": "다운로드파일 업로드할 BucketName"
  }
```

### 4) Email Notifiation 설정 (향후 SES 통해 이메일이 발송될 수 있도록 설정함)
  - SNS(Simple Notification Service) Topics 생성
  - Subscriptions에서 신규 생성해서 위에서 생성한 Topic의 ARN에 Email Protocol로, 실제 받을 이메일 주소를 Endpoint로 설정
  - 위에서 입력한 이메일 계정에서 Subscription 활성화

### 5) S3 bucket 내 대상 File 업로드되면 자동으로 Trigger되어 이메일 발송하는 Lambda Function 생성
  - S3를 Trigger 설정, 2)단계에서 업로드되는 S3 Bucket 내 ObjectCreated Event type으로 지정
  - Memory, Timeout 기본 설정, Role은 Lambda basic role에 AmazonS3FullAccess, AmazonSNSFullAccess 추가
  - Fuction code에 Lambda_function_mailsender.py 내 code 추가
    TopicArn='arn:aws:sns:ap-northeast-2:xxx', 이 부분에 4)단계에서 생성한 SNS Topic의 Arn을 넣어줌
 
