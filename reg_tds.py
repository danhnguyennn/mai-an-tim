from threading import Thread
from time import sleep
from models.tdsModel import API_TDS
from models.captcha import bypassCaptcha


APIKEY = '8a903bef4fde456181419c31e6eb3325'
def regAccount(username, password):
    tds = API_TDS('')
    g_captcha = bypassCaptcha(APIKEY)
    reg = tds.regTds(g_captcha, username, password)
    print(username, reg)
    if "success" in str(reg):
        with open('account.txt', 'a', encoding='utf-8') as save:
            save.write(f"{username}|{password}\n")

so_tu = 1
so_stop = 21
name = 'xoai000'
password = 'Nhinqq#'
for i in range(so_tu, so_stop+1):
    username = name+str(i)
    Thread(target=regAccount, args=(username, password, )).start()
    sleep(1)

