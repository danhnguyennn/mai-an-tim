from onest_captcha import OneStCaptchaClient
import requests
from time import sleep

from models.proxyModel import GenProxy

def stCaptcha(APIKEY):
    for i in range(2):
        client = OneStCaptchaClient(apikey=APIKEY)
        result = client.recaptcha_v2_task_proxyless(site_url="https://traodoisub.com/view/chtiktok/", site_key="6LeGw7IZAAAAAECJDwOUXcriH8HNN7_rkJRZYF8a", invisible=False)
        try:
            return result["token"]
        except: pass
    return False

def omoCaptcha(APIKEY):
    for i in range(2):
        data = {
            "api_token": APIKEY,
            "data": {
                "type_job_id": "1",
                "website_url": "https://traodoisub.com/view/chtiktok/",
                "website_key": "6LeGw7IZAAAAAECJDwOUXcriH8HNN7_rkJRZYF8a",
                "isInvisible": False
            }
        }
        client = requests.post('https://omocaptcha.com/api/createJob', json=data).json()
        status = client['error']
        if status == False:
            job_id = client['job_id']
            print(job_id)
            data2 = {
                "api_token": APIKEY,
                "job_id": job_id
            }
            for i in range(60):
                result = requests.post('https://omocaptcha.com/api/getJobResult', json=data2).json()
                print(result)
                # status2 = result['status']
                # print(status2)
                # # return
                # if status2 == 'success':
                #     result_token = result['result']
                #     return result_token
                sleep(2)

def captcha69(APIKEY):
    for _ in range(2):
        try:
            get_id = requests.post(f'https://captcha69.com/in.php?key={APIKEY}&googlekey=6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-&method=userrecaptcha&pageurl=https://www.google.com%2Frecaptcha%2Fapi2%2Fdemo').text
            id_job = get_id.split('|')[1]
            for _ in range(80):
                result = requests.post(f'https://captcha69.com/res.php?key={APIKEY}&action=get&id={id_job}').text
                try:
                    token = result.split('|')[1]
                    return token
                except:
                    sleep(2)
        except: pass

def capMonsterCloud(APIKEY):
    for _ in range(2):
        proxie = GenProxy().getProxy()
        try:
            data = {
                "clientKey": APIKEY,
                "task": 
                {
                    "type":"NoCaptchaTaskProxyless",
                    "websiteURL":"https://traodoisub.com/view/chtiktok/",
                    "websiteKey":"6LeGw7IZAAAAAECJDwOUXcriH8HNN7_rkJRZYF8a"
                }
            }
            create_task = requests.post('https://api.capmonster.cloud/createTask', json=data, proxies=proxie, timeout=10).json()
            # print(create_task)
            errorId = create_task['errorId']
            if errorId == 0:
                taskId = create_task['taskId']
                data_task = {
                    "clientKey": APIKEY,
                    "taskId": taskId
                }
                for _ in range(100):
                    result = requests.post('https://api.capmonster.cloud/getTaskResult/', json=data_task, proxies=proxie, timeout=10).json()
                    # print(result)
                    status = result['status']
                    if status == 'ready':
                        token = result['solution']['gRecaptchaResponse']
                        return token
                    sleep(3)
        except: pass

def guruCaptcha(APIKEY):
    for _ in range(2):
        try:
            response = requests.post(f'http://api.cap.guru/in.php?key={APIKEY}&method=userrecaptcha&googlekey=6LeGw7IZAAAAAECJDwOUXcriH8HNN7_rkJRZYF8a&pageurl=https://traodoisub.com/view/chtiktok/').text
            print(response)
            idJob = response.split('|')[1]
            json_data = {
                "key": APIKEY,
                "action": "get",
                "id": idJob, 
                "json": 1
            }
            for _ in range(60):
                result = requests.post('http://api.cap.guru/res.php', json=json_data).json()
                print(result)
                status = result['status']
                if status == 1:
                    token = result['request']
                    return token
                sleep(3)
        except: pass
        
def bypassCaptcha(APIKEY, site='1st'):
    if site == '1st':
        token = stCaptcha(APIKEY)
    elif site == 'ct69':
        token = captcha69(APIKEY)
    elif site == 'omo_ct':
        token = omoCaptcha(APIKEY)
    elif site == 'cloud_cap':
        token = capMonsterCloud(APIKEY)
    elif site == 'guru':
        token = guruCaptcha(APIKEY)
    return token

# g_response = bypassCaptcha('7d3b1901f9ff0dd7b07621840e84f3db', 'guru')
# print(g_response)