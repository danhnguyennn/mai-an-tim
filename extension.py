import string
import requests
from time import sleep
import threading
import random
import concurrent.futures
from colorama import init, Fore

from models.tdsModel import API_TDS
from models.proxyModel import GenProxy

init(autoreset=True)
CEND      = '\33[0m'
CBOLD     = '\33[1m'
CITALIC   = '\33[3m'
CURL      = '\33[4m'
CBLINK    = '\33[5m'
CBLINK2   = '\33[6m'
CSELECTED = '\33[7m'

CBLACK  = '\33[30m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CVIOLET = '\33[35m'
CBEIGE  = '\33[36m'
CWHITE  = '\33[37m'

CBLACKBG  = '\33[40m'
CREDBG    = '\33[41m'
CGREENBG  = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG   = '\33[44m'
CVIOLETBG = '\33[45m'
CBEIGEBG  = '\33[46m'
CWHITEBG  = '\33[47m'

CGREY    = '\33[90m'
CRED2    = '\33[91m'
CGREEN2  = '\33[92m'
CYELLOW2 = '\33[93m'
CBLUE2   = '\33[94m'
CVIOLET2 = '\33[95m'
CBEIGE2  = '\33[96m'
CWHITE2  = '\33[97m'

CGREYBG    = '\33[100m'
CREDBG2    = '\33[101m'
CGREENBG2  = '\33[102m'
CYELLOWBG2 = '\33[103m'
CBLUEBG2   = '\33[104m'
CVIOLETBG2 = '\33[105m'
CBEIGEBG2  = '\33[106m'
CWHITEBG2  = '\33[107m'

def randStr(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
class Exten():
    def __init__(self) -> None:
        self.tds = API_TDS()
        self.prx = GenProxy()

    def settingTool(self):
        return int(input("[1] : Check trùng dữ liệu 1 filen\n[2] : Check trùng dữ liệu 2 file\n[3] : Check xu account tds\n[4] : Change Password TDS\n[5] : Check live tiktok\nChọn: "))
    
    def checkDupFileAccount(self):
        print("Check trùng dữ liệu file account.txt")
        with open('account.txt', 'r') as file:
            arr_account = file.readlines()

        seen_accounts = set()

        for account in arr_account:
            username, password, noti = account.split("|")
            account_key = f"{username}|{password}"
            if account_key in seen_accounts:
                print(f"Duplicate Account: {account.strip()}")
            else:
                seen_accounts.add(account_key)
                with open('data_check\\checked.txt', 'a+') as file:
                    file.write(account)
        print("Dữ liệu được lọc và lưu ở data_check/checked.txt")
    def checkDupTwoFile(self):
        print("Check trùng dữ liệu 2 file")
        with open('data_check\\file1.txt', 'r') as file1, open('data_check\\file2.txt', 'r') as file2:
            data1 = set(file1.read().splitlines())
            data2 = set(file2.read().splitlines())
        
        for f2 in data2:
            username, password, noti = f2.split("|")
            account_key = f"{username}|{password}"
            if account_key in str(data1):
                print(f"Duplicate Account: {f2.strip()}")
            else:
                with open('data_check\\check_two_file.txt', 'a+') as file:
                    file.write(f2 + '\n')
        print("Dữ liệu được lọc và lưu ở data_check/check_two_file.txt")
    def mainChangePwd(self, user_tds, pwd_tds):
        newpass = randStr(8)
        change = self.tds.changePass(user_tds, pwd_tds, newpass)
        if change:
            print(f"{user_tds}|{pwd_tds}|{newpass}|SUCCESS")
        else:
            print(f"{user_tds}|{pwd_tds}|{newpass}|FAILED")
    def checkLiveTiktok(self, account, user_tiktok):
        for _ in range(2):
            proxie = self.prx.getProxy()
            check = requests.get(f'https://countik.com/api/exist/{user_tiktok}', timeout=10, proxies=proxie).json()
            try:
                with open('data_check\\tiktok_live.txt', 'a+') as file:
                    file.write(account)
                return print(CGREEN + f"{check['id']} : {user_tiktok} : LIVE")
            except: pass
        print(CRED + f"None : {user_tiktok} : DIE")
    def checkAccount(self, usertds, passwdtds):
        ss = requests.Session()
        proxie = self.prx.getProxy()
        data = {
            'username': usertds,
            'password': passwdtds,
        }
        try:
            home = ss.post('https://traodoisub.com/scr/login.php', data=data, proxies=proxie, timeout=10).text
            user_info = ss.get('https://traodoisub.com/scr/user.php', proxies=proxie, timeout=10).json()
            print(home, f"{usertds}|{passwdtds}|{user_info['xu']}")
        except:
            print(usertds, "FAIL")

    def threadToolTds(self, number):
        with open('account.txt', 'r', encoding='utf-8') as file:
            arr_account = file.readlines()

        for acc in arr_account:
            user_tds = acc.split('|')[0]
            pwd_tds = acc.split('|')[1]
            if number == 3:
                threading.Thread(target=self.checkAccount, args=(user_tds, pwd_tds, )).start()
            elif number == 4:
                self.mainChangePwd(user_tds, pwd_tds, )
            sleep(0.5)
    def threadCheckLive(self):
        with open('account.txt', 'r', encoding='utf-8') as file:
            arr_account = file.readlines()
        threads = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for acc in arr_account:
                user_tiktok = acc.split('|')[2].strip()
                futures.append(executor.submit(self.checkLiveTiktok, acc, user_tiktok))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
        print("Dữ liệu được lọc và lưu ở data_check/tiktok_live.txt")


    def mainTool(self):
        number = self.settingTool()
        if number == 1:
            self.checkDupFileAccount()
        elif number == 2:
            self.checkDupTwoFile()
        elif number == 3 or number == 4:
            self.threadToolTds(number)
        elif number == 5:
            self.threadCheckLive()
        else:
            print("Không có chức năng trên")



Exten().mainTool()