from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import boto3
import os
import time

def lambda_handler(event, context):

    print("Starting")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.add_argument('--user-data-dir=/tmp/user-data')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir=/tmp')
    chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
    chrome_options.add_argument("lang=ko_KR") # 한국어!
    chrome_options.binary_location = "/opt/python/headless-chromium"


    # Browser Launch - headless
    driver = webdriver.Chrome('/opt/python/chromedriver', options=chrome_options)
    driver.implicitly_wait(3)

    # File Download 설정
    download_dir = "/tmp"
    driver.command_executor._commands["send_command"] = (
        "POST",
        '/session/$sessionId/chromium/send_command'
    )
    params = {
        'cmd': 'Page.setDownloadBehavior',
        'params': {
            'behavior': 'allow',
            'downloadPath': download_dir
        }
    }
    driver.execute("send_command", params)

    # ID/PW 설정
    id = event['id']
    pwd = event['pwd']

    # Page 접속 -> Login 페이지로 Redirect
    driver.get("https://asset.opsnow.com/#/rsrc-optm/summary")
    driver.implicitly_wait(20)
    print(driver.title)

    # Login 되어 있지 않으면 Login
    if driver.title == "OpsNow" :
        elem = driver.find_element_by_id("username")
        elem.send_keys(id)
        #driver.implicitly_wait(3)
        elem = driver.find_element_by_id("password")
        elem.send_keys(pwd)

        #driver.implicitly_wait(3)
        driver.find_element_by_name("login").click()
        driver.implicitly_wait(30)

    # File download
    print(driver.title)
    driver.find_element_by_xpath("/html/body/app/div/main/bg-asset-rsrc-opti-main/div/bg-asset-summary/div/aside/div/bg-asset-cost-optimization-report-download/div/div/ul/li[1]/button").click()
    # Download 시간 확보
    time.sleep(30)

    driver.quit()

    # S3 upload
    s3 = boto3.resource('s3')
    upload_filename = '/tmp/ANALYSIS-REPORT.xlsx'
    bucket_name = event['bucket']
    key_name = 'ANALYSIS-REPORT.xlsx'
    response = s3.meta.client.upload_file(upload_filename, bucket_name, key_name)

    return response
