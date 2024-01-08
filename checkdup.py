import requests
from time import sleep
import threading
import random

class Exten():
    def __init__(self) -> None:
        pass

    def settingTool(self):
        return int(input("[1] : Check trùng dữ liệu 1 filen\n[2] : Check trùng dữ liệu 2 file\n[3] : Check xu account tds\nChọn: "))
    def getProxy():
        with open('data\\proxy\\proxy.txt', 'r', encoding='utf-8') as file:
            arr_proxy = file.readlines()
        if len(arr_proxy) > 0:
            proxie = random.choice(arr_proxy).strip()
            splitProxy = proxie.split(':')
            host = splitProxy[0]
            port = splitProxy[1]
            user = splitProxy[2]
            pwd = splitProxy[3]
            return {'https': f'http://{user}:{pwd}@{host}:{port}'}
        else:
            return {}
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

    def checkAccount(self, usertds, passwdtds):
        ss = requests.Session()
        proxie = self.getProxy()
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
    def threadToolTds(self):
        with open('account.txt', 'r', encoding='utf-8') as file:
            arr_account = file.readlines()

        for acc in arr_account:
            user_tds = acc.split('|')[0]
            pwd_tds = acc.split('|')[1]
            threading.Thread(target=self.checkAccount, args=(user_tds, pwd_tds, )).start()
            sleep(0.5)

    def mainTool(self):
        number = self.settingTool()
        if number == 1:
            self.checkDupFileAccount()
        elif number == 2:
            self.checkDupTwoFile()
        elif number == 3:
            self.threadToolTds()
        else:
            print("Không có chức năng trên")



Exten().mainTool()