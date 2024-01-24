import requests
import time
from models.proxyModel import GenProxy

ss = requests.Session()
with open('account.txt', 'r', encoding='utf-8') as file:
    account = file.readlines()

# supinnsoz1044|123|10002200


with open('thongke.txt', 'a+', encoding='utf-8') as output_file:
    total_xu = 0
    user_dep = "supinnsoz1044"
    total_xuall = 0
    for acc in account:
        proxie = GenProxy().getProxy()
        try:
            user = acc.split('|')[0]
            pwd = acc.split('|')[1].strip()
            data = {
                'username': user,
                'password': pwd,
            }
            ss.post('https://traodoisub.com/scr/login.php', data=data, proxies=proxie)
            user_info = ss.get('https://traodoisub.com/scr/user.php' , timeout=10, proxies=proxie).json()
            
            if 'xu' in user_info:
                xu = int(user_info['xu'])
                if xu > 1000000:
                    fee1 = xu * 9.1 / 100
                    fee = str(int(fee1))
                    # adjusted_xu = xu - fee1
                    adjusted_xu = 5000000
                    total_xu += adjusted_xu
                    total_xuall += xu
                    
                    adjusted_xu_str = str(int(adjusted_xu))
                    # print(f'Xu {data["username"]}: ', xu, f'Có thể chuyển : ', adjusted_xu_str)
                    with open('thongke.txt','a+',encoding='utf-8') as file:
                          file.write(f'{user}|{pwd}|{xu}\n')
                    # xu_send = input("Nhập xu send ( fee: 10% ): ")
                    data = {
                        'usernhan': user_dep,
                        'xutang': int(adjusted_xu),
                    }
                    response = ss.post('https://traodoisub.com/view/tangxu/tangxu.php', data=data, timeout=10, proxies=proxie).text
                    print(f'Xu {user}: ', xu, f'Đã send : ', adjusted_xu_str)
                    # print(response)
                    # time.sleep(10)
                else:
                     with open('chuaduxu.txt','a+',encoding='utf-8') as file:
                          file.write(f'{user}|{pwd}|{xu}\n')
        except:
            pass
    total_xuall_str  = str(int(total_xuall))
    total_xu_str = str(int(total_xu))

    print(f'Tổng xu {total_xuall_str} , trừ fee ->>  ', total_xu_str)
    output_file.write(f'Tổng xu {total_xuall_str} , trừ fee ->>   {total_xu_str}\n')

