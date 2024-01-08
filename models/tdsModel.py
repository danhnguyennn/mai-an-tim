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
        self.check_proxy = 0
        
    def getProxy(self):
        if self.check_proxy >= 10:
            return {}
        if len(self.arr_proxy) > 0:
            proxie = random.choice(self.arr_proxy).strip()
            splitProxy = proxie.split(':')
            host = splitProxy[0]
            port = splitProxy[1]
            user = splitProxy[2]
            pwd = splitProxy[3]
            self.check_proxy = 0
            return {'https': f'http://{user}:{pwd}@{host}:{port}'}
        else:
            time.sleep(3)
            self.check_proxy += 1
            with open('data\\proxy\\proxy.txt', 'r', encoding='utf-8') as file:
                self.arr_proxy = file.readlines()
            return self.getProxy()
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
        for _ in range(10):
            try:
                self.ss.post('https://traodoisub.com/scr/login.php', data=data, proxies=proxie, timeout=10)
                user = self.ss.get('https://traodoisub.com/view/setting/load.php', proxies=proxie, timeout=10).json()
                user_info = self.ss.get('https://traodoisub.com/scr/user.php', proxies=proxie, timeout=10).json()
                return {
                    'xu': '{:,}'.format(int(user_info['xu'])),
                    'access_token': user['tokentds']
                }
            except:
                proxie = self.checkProxy()
        return {}
    def cauHinhTds(self, g_captcha_result, username, usertds, passwdtds, proxie={}):
        proxie = self.checkProxy()
        data = {
            'username': usertds,
            'password': passwdtds,
        }
        try:
            self.ss.post('https://traodoisub.com/scr/login.php', data=data, proxies=proxie, timeout=10)
            cauhinh = self.ss.get('https://traodoisub.com/view/chtiktok/', proxies=proxie, timeout=10).text
            if username not in cauhinh:
                data = {
                    'idfb': username,
                    'g-recaptcha-response': g_captcha_result
                }
                ch = self.ss.post('https://traodoisub.com/scr/tiktok_add.php', data=data, proxies=proxie, timeout=10).json()
                print(username, ch)
                if 'Tài khoản ở chế độ riêng tư' in str(ch):
                    return 'private'
                elif 'cập nhật ảnh đại diện' in str(ch):
                    return 'defaut_avatar'
                elif 'tiktok không tồn tại' in str(ch):
                    return 'not_account'
            for _ in range(5):
                try:
                    response = requests.get(f"https://traodoisub.com/api/?fields=tiktok_run&id={username}&access_token={self.access_token}", proxies=proxie, timeout=10).json()
                    break
                except:
                    proxie = self.checkProxy()
            print(username, response)
            if "uniqueID" in response["data"] and response["data"]["uniqueID"] == username:
                return True
        except Exception as e:
            print("ERR", e)
            return False
    def getJobTds(self, type_job='tiktok_follow'):
        proxie = self.checkProxy()
        for i in range(5):
            try:
                response = requests.get(f"https://traodoisub.com/api/?fields={type_job}&access_token={self.access_token}", proxies=proxie, timeout=10).json()
                if 'Thao tác quá nhanh' in str(response):
                    return False
                elif response['data'] == []:
                    return False
                return response
            except:
                proxie = self.checkProxy()
        return False
    def checkCacheJob(self, cache_job, idjob):
        proxie = self.checkProxy()
        for i in range(5):
            try:
                response = requests.get(f"https://traodoisub.com/api/coin/?type={cache_job}&id={idjob}&access_token={self.access_token}", proxies=proxie, timeout=10).json()
                return response
            except:
                proxie = self.checkProxy()
        return False
    def submitJobFollow(self, type_api):
        proxie = self.checkProxy()
        for i in range(5):
            try:
                response = requests.get(f"https://traodoisub.com/api/coin/?type={type_api}&access_token={self.access_token}", proxies=proxie, timeout=10).json()
                return response
            except Exception as e:
                s = repr(e)
                if 'Cannot connect to proxy' in s or 'certificate verify failed' in s or 'Read timed out.' in s:
                    proxie = self.checkProxy()
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
        for i in range(5):
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
                proxie = self.checkProxy()
        return False