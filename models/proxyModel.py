from time import sleep
import requests
import random
from time import sleep

class GenProxy():
    def __init__(self):
        with open('data\\proxy\\proxy.txt', 'r', encoding='utf-8') as file:
            self.arr_proxy = file.readlines()
        self.allow_ip = requests.get('https://icanhazip.com').text.strip()
        # self.allow_ip = '171.250.246.88'
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
            sleep(3)
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
                sleep(2)
        return {}
    # shop like
    def Shoplike(self, key):
        try:
            get = requests.get(f'http://proxy.shoplike.vn/Api/getNewProxy?access_token={key}&location=&provider=').json()
            proxy = get['data']['proxy']
            return proxy
        except:
            return False
    def getCurrentIPShoplike(self, key):
        try:
            get = requests.get(f'http://proxy.shoplike.vn/Api/getCurrentProxy?access_token='+key).json()
            print(get)
            proxy = get['data']['proxy']
            return proxy
        except:
            return False
    def ChangeProxyShopLike(self, key):
        while True:
            prx = self.Shoplike(key)
            if prx: return prx
            sleep(10)
    #  dt proxy
    def DTProxy(self, key):
        try:
            get = requests.get(f'https://app.proxydt.com/api/public/proxy/get-new-proxy?license={key}&authen_ips={self.allow_ip}', headers={"Accept":"application/json", "Content-Type":"application/json"}).json()
            # print(get)
            proxy = get['data']['http_ipv4'].replace('http://', '')
            return proxy
        except:
            return False
    def getCurrentIPDTProxy(self, key):
        try:
            get = requests.get(f'https://app.proxydt.com/api/public/proxy/get-current-proxy?license={key}&authen_ips={self.allow_ip}').json()
            # print(get)
            proxy = get['data']['http_ipv4'].replace('http://', '')
            return proxy
        except:
            return False
    def ChangeProxyDTProxy(self, key):
        while True:
            prx = self.DTProxy(key)
            print("Changing proxy ...", end='\r')
            if prx: return prx
            sleep(10)
    # tinsoft
    def Tinsoft(self, keyPrx):
        try:
            ip = requests.get(f'https://proxy.tinsoftsv.com/api/changeProxy.php?key={keyPrx}&location=0').json()
            proxy = ip['proxy']
            return proxy
        except:
            return False
    def getCurrentIPTinsoft(self, key):
        try:
            get = requests.get(f'http://proxy.tinsoftsv.com/api/getProxy.php?key={key}').json()
            proxy = get['proxy']
            return proxy
        except:
            return False
    def ChangeProxyTinsoft(self, key):
        while True:
            prx = self.Tinsoft(key)
            if prx: return prx
            sleep(10)
    # min proxy
    def MinProxy(self, key):
        try:
            get = requests.get(f'https://dash.minproxy.vn/api/rotating/v1/proxy/get-new-proxy?api_key={key}').json()
            http_proxy = get['data']['http_proxy']
            username = get['data']['username']
            password = get['data']['password']
            proxy = f'{username}:{password}@{http_proxy}'
            return proxy
        except:
            return False
    def getCurrentIPMinProxy(self, key):
        try:
            get = requests.get(f'https://dash.minproxy.vn/api/rotating/v1/proxy/get-current-proxy?api_key={key}').json()
            http_proxy = get['data']['http_proxy']
            username = get['data']['username']
            password = get['data']['password']
            proxy = f'{username}:{password}@{http_proxy}'
            return proxy
        except:
            return False
    def ChangeProxyMin(self, key):
        while True:
            prx = self.MinProxy(key)
            if prx: return prx
            sleep(10)
    # tm proxy
    def TmProxy(self, key):
        try:
            data = '{\"api_key\":\"'+key+'\",\"sign\":\"string\",\"id_location\":0}'
            get = requests.post('https://tmproxy.com/api/proxy/get-new-proxy', data=data, headers={"accept": "application/json", "Content-Type": "application/json"}).json()
            print(get)
            proxy = get['data']['https']
            return proxy
        except:
            return False
    def getCurrentIPTmProxy(self, key):
        try:
            data = '{\"api_key\":\"1453385cf1b65cd82f0174dc57bbea31\"}'
            get = requests.post('https://tmproxy.com/api/proxy/get-current-proxy', data=data).json()
            proxy = get['data']['https']
            return proxy
        except:
            return False
    def ChangeProxyTm(self, key):
        while True:
            prx = self.TmProxy(key)
            if prx: return prx
            sleep(10)
    # proxyno1
    def ProxyNo1(self, key):
        try:
            get = requests.get('https://app.proxyno1.com/api/change-key-ip/'+key).json()
            print(get, end='\r')
            if get['status'] == 0: return True
        except:
            return False
    def ChangeProxyNo1(self, key):
        while True:
            prx = self.ProxyNo1(key)
            if prx: return prx
            sleep(10)
    # proxyv6
    def ProxyV6(self, key, ipv4):
        ipv4 = '116.110.42.62'
        try:
            get = requests.get(f'https://api.proxyv6.net/key/get-new-ip?api_key_rotating={key}&authIp={ipv4}').json()
            host = get['data']['host']
            port = get['data']['port']
            proxy = host+':'+str(port)
            return proxy
        except:
            return False
    def ChangeProxyV6(self, key):
        while True:
            prx = self.ProxyV6(key)
            if prx: return prx
            sleep(10)
    # mobi proxy
    def checkResetMobiProxy(self, proxys):
        ips = proxys.split(":")[0]
        try:
            if "ok" in str(requests.get("http://"+ips+"/proxy_getip?proxy="+proxys).text):
                return True
        except: pass
    # wwproxy
    def Wwproxy(self, key):
        try:
            get = requests.get(f'https://wwproxy.com/api/client/proxy/available?key={key}&provinceId=-1').json()
            print(get, end='\r')
            status = get['status']
            if status == 'OK':
                proxy = get['data']['proxy']
                return proxy
        except:
            return False
        




# a = GenProxy().Wwproxy('6146a566-4138-419e-bde6-48affe27dcbc')
# print(a)

# proxie = {
#     'https': 'http://'+a}
# ip = requests.get('https://api.myip.com', proxies=proxie).text
# print(ip)
