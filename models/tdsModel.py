import traceback
import requests
import time
import random

class API_TDS:
    def __init__(self, access_token='') -> None:
        with open('data\\proxy\\proxy.txt', 'r', encoding='utf-8') as file:
            self.arr_proxy = file.readlines()
        self.ss = requests.Session()
        self.access_token = access_token
    def getProxy(self):
        if len(self.arr_proxy) > 0:
            proxie = random.choice(self.arr_proxy).strip()
            splitProxy = proxie.split(':')
            host = splitProxy[0]
            port = splitProxy[1]
            user = splitProxy[2]
            pwd = splitProxy[3]
            return {'https': f'http://{user}:{pwd}@{host}:{port}'}
        else:
            return {}
    def checkProxy(self):
        for i in range(10):
            proxy = self.getProxy()
            try:
                requests.get('https://api.ipify.org?format=json', proxies=proxy, timeout=10)
                return proxy
            except:
                time.sleep(2)
        return {}
    def getTokenTds(self, usertds, pwdtds):
        proxie = self.checkProxy()
        data = {
            'username': usertds,
            'password': pwdtds,
        }
        try:
            self.ss.post('https://traodoisub.com/scr/login.php', data=data, proxies=proxie, timeout=10)
            user = self.ss.get('https://traodoisub.com/view/setting/load.php', proxies=proxie, timeout=10).json()
            user_info = self.ss.get('https://traodoisub.com/scr/user.php', proxies=proxie, timeout=10).json()
            return {
                'xu': '{:,}'.format(int(user_info['xu'])),
                'access_token': user['tokentds']
            }
        except:
            return {}
    def cauHinhTds(self, g_captcha_result, username, usertds, passwdtds, proxie={}):
        proxie = self.checkProxy()
        data = {
            'username': usertds,
            'password': passwdtds,
        }
        for i in range(10):
            try:
                self.ss.post('https://traodoisub.com/scr/login.php', data=data, proxies=proxie, timeout=10)
                user = self.ss.get('https://traodoisub.com/view/setting/load.php', proxies=proxie, timeout=10).json()
                token = user['tokentds']
                cauhinh = self.ss.get('https://traodoisub.com/view/cauhinh/', proxies=proxie, timeout=10).text
                if username not in cauhinh:
                    data = {
                        'idfb': username,
                        'g-recaptcha-response': g_captcha_result
                    }
                    self.ss.post('https://traodoisub.com/scr/tiktok_add.php', data=data, proxies=proxie, timeout=10)
                    response = requests.get(f"https://traodoisub.com/api/?fields=tiktok_run&id={username}&access_token={token}", proxies=proxie, timeout=10)
                    data = response.json()
                    if "uniqueID" in data["data"] and data["data"]["uniqueID"] == username:
                        return True
            except:
                self.checkProxy()
                time.sleep(2)
        return False
    def getJobTds(self, type_job='tiktok_follow', proxie={}):
        for i in range(5):
            try:
                response = requests.get(f"https://traodoisub.com/api/?fields={type_job}&access_token={self.access_token}", proxies=proxie, timeout=10).json()
                return response
            except Exception as e:
                s = repr(e)
                if 'Cannot connect to proxy' in s or 'certificate verify failed' in s or 'Read timed out.' in s:
                    proxie = self.checkProxy()
                time.sleep(2)
        return False
    def checkCacheJob(self, cache_job, idjob, proxie={}):
        for i in range(5):
            try:
                response = requests.get(f"https://traodoisub.com/api/coin/?type={cache_job}&id={idjob}&access_token={self.access_token}", proxies=proxie, timeout=10).json()
                return response
            except Exception as e:
                s = repr(e)
                if 'Cannot connect to proxy' in s or 'certificate verify failed' in s or 'Read timed out.' in s:
                    proxie = self.checkProxy()
                time.sleep(2)
        return False
    def submitJobFollow(self, type_api, proxie={}):
        for i in range(5):
            try:
                response = requests.get(f"https://traodoisub.com/api/coin/?type={type_api}&access_token={self.access_token}", proxies=proxie, timeout=10).json()
                return response
            except Exception as e:
                s = repr(e)
                if 'Cannot connect to proxy' in s or 'certificate verify failed' in s or 'Read timed out.' in s:
                    proxie = self.checkProxy()
                time.sleep(2)
        return False
    def sendXu(self, user, pwd, usernhan, xu_send):
        proxie = self.checkProxy()
        try:
            data = {
                'username': user,
                'password': pwd,
            }
            self.ss.post('https://traodoisub.com/scr/login.php', data=data, proxies=proxie, timeout=10)
            user = self.ss.get('https://traodoisub.com/scr/user.php', proxies=proxie, timeout=10).json()
            data = {
                'usernhan': usernhan,
                'xutang': xu_send,
            }
            response = self.ss.post('https://traodoisub.com/view/tangxu/tangxu.php', data=data, proxies=proxie, timeout=10).text
            return response
        except:
            tb = traceback.format_exc()
            return tb
    def regTds(self, g_captcha_result, username, password):
        proxie = self.checkProxy()
        try:
            data = {
                'dkusername': username,
                'dkpassword': password,
                'rdkpassword': password,
                'g-recaptcha-response': g_captcha_result,
            }

            response = requests.post('https://traodoisub.com/scr/check_reg.php', data=data, proxies=proxie, timeout=10).json()['success']
            return username
        except:
            return False
    def changePass(self, usertds, pwdtds, newpass):
        proxie = self.checkProxy()
        data = {
            'username': usertds,
            'password': pwdtds,
        }
        try:
            self.ss.post('https://traodoisub.com/scr/login.php', data=data, proxies=proxie, timeout=10)
            data = {
                'oldpass': pwdtds,
                'newpass': newpass,
                'renewpass': newpass,
            }
            response = self.ss.post('https://traodoisub.com/scr/doipass.php', data=data, proxies=proxie, timeout=10).text
            print(response)
            if response == '0':
                return True
            return False
        except:
            return False


# a = API_TDS('TDS9JyMyVmdlNnI6IiclZXZzJCLiATM4IDauFGZiojIyV2c1Jye').getJobTds('tiktok_like')
# print(type(a), a)
# cache = a['cache']

#     print(job['id'])

# a = {'cache': 0, 'data': [{'id': '7299772387753512210_G85D9JXOK9TTNBJKM3M0', 'link': 'https://www.tiktok.com/@miuuxink08/video/7299772387753512210', 'type': 'like'}, {'id': '7300168784072002823_A08GOFAHDM6RGUPLEI4A', 'link': 'https://www.tiktok.com/@nhumanhstore/video/7300168784072002823', 'type': 'like'}, {'id': '7301498696514997511_TJTN61XORBDJ9Z72P969', 'link': 'https://www.tiktok.com/@nhanhoang.top1trader/video/7301498696514997511', 'type': 'like'}, {'id': '7299859179148168449_3FS0BGO4O29Y6LP1ZS6Z', 'link': 'https://www.tiktok.com/@pvcombankofficial/video/7299859179148168449', 'type': 'like'}, {'id': '7301575987400133895_CK0OYDONUR2YL2QEY7OG', 'link': 'https://www.tiktok.com/@cherrybyjen/video/7301575987400133895', 'type': 'like'}, {'id': '7301583776054906119_IQ87K8RJULOQWIRTNJXN', 'link': 'https://www.tiktok.com/@toiyeuvietnam121231/video/7301583776054906119', 'type': 'like'}, {'id': '7301360960416058642_MTBA4OUX9T9CHAS5CX80', 'link': 'https://www.tiktok.com/@quanghuy796879/video/7301360960416058642', 'type': 'like'}, {'id': '7301739584730303751_1L9V65MJB45WF2B195DU', 'link': 'https://www.tiktok.com/@le.lam0210/video/7301739584730303751', 'type': 'like'}, {'id': '7299360475505102081_BSPAYQIVOD7MY8U7838Y', 'link': 'https://www.tiktok.com/@nthw2303/video/7299360475505102081', 'type': 'like'}, {'id': '7301939845256039688_X3FNOM5SIIA13UFCDD5Q', 'link': 'https://www.tiktok.com/@woowoan.deyy/video/7301939845256039688', 'type': 'like'}]}
# job = a['data']
# while True:
#     # for i, job in enumerate(a['data']):
#     idlike = job[0]['id']
#     print(idlike)
#     a['data'].pop(0)

#     print(a)
