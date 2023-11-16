import requests, time
from threading import Thread

with open('data\\proxy\\proxy.txt', 'r', encoding='utf-8') as file:
    arr_proxy = file.readlines()

def check(proxy):
    try:
        requests.get('https://api.ipify.org?format=json', proxies=proxy, timeout=10)
        print(proxy, "Live")
    except:
        print(proxy, "Die")


for i in range(len(arr_proxy)):
    proxie = arr_proxy[0].strip()
    splitProxy = proxie.split(':')
    host = splitProxy[0]
    port = splitProxy[1]
    user = splitProxy[2]
    pwd = splitProxy[3]
    proxy = {'https': f'http://{user}:{pwd}@{host}:{port}'}
    Thread(target=check, args=(proxy, )).start()
    # time.sleep(1)
    arr_proxy.remove(arr_proxy[0])
        