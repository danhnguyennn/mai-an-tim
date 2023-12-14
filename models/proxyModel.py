import random
from time import sleep

class GenProxy():
    def __init__(self):
        with open('data\\proxy\\proxy.txt', 'r', encoding='utf-8') as file:
            self.arr_proxy = file.readlines()
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

