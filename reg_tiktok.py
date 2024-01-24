from datetime import datetime
import os
import json
import threading
import traceback
import random
import urllib.request
from time import sleep
from threading import Thread
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from models.gpmModels import API_GPM
from models.captcha import captchaTiktok
from models.proxyModel import GenProxy

with open('reg\\mail_reg.txt', 'r', encoding='utf-8') as file:
    list_email = file.read().split('\n')

def getMail():
    if len(list_email) > 0:
        dtMail = list_email[0]
        list_email.pop(0)
        open('reg\\mail_reg.txt', 'w').write('\n'.join(list_email))
        return dtMail
    else:
        return False
def postMail(account):
    data = {"account": account}
    response = requests.post('http://127.0.0.1:5000/api/data', json=data)
    return response.json()
class RegTiktok():
    def __init__(self):
        with open('config\\config.json', 'r', encoding='utf-8-sig') as file:
            file_config = json.loads(file.read())
            URL = file_config['URL']
        self.gpm = API_GPM(URL)
        self.api_proxie = GenProxy()
        self.API_KEY = file_config['key_captcha'] # key captcha
        self.path_image = file_config['PATH_IMG'] # đường dẫn ảnh
        self.remaining = file_config['REMAINING'] # số lượng còn lại
        self.lock = threading.Lock()

    def checkAndDelePro5(self):
        group_name = 'test'
        group = self.gpm.GPM_ListGroupv3()
        for gr in group['data']:
            if group_name == gr['name']:
                group_id = gr['id']
                break
        arr_profile = self.gpm.GPM_ListProfilev3(group_id)['data']
        # 
        for pro5 in arr_profile:
            profile_id = pro5['id']
            self.gpm.GPM_DeleteProfilev3(profile_id)

    def setupChrome(self, profile_id, x, dpi, toa_x):
        try:
            start_profile = self.gpm.GPM_StartProfilev3(profile_id, x, dpi, toa_x)
            sleep(3)
            options = Options()
            options.debugger_address = start_profile['data']['remote_debugging_address']
            options.add_argument('--disable-javascript')
            driver = webdriver.Chrome(start_profile['data']['driver_path'], options=options)
            return driver
        except Exception as e:
            err = traceback.format_exc()
            print(err)
            if 'cannot determine loading status' in err:
                return 'loading'
            return 'Exception'
    def chromeTest(self):
        options = Options()
        options.debugger_address = '127.0.0.1:52540'
        driver = webdriver.Chrome("C:\\Users\\ndanh\\AppData\\Local\\Programs\\GPMLogin\\gpm_browser\\gpm_browser_chromium_core_119\\gpmdriver.exe", options=options)
        return driver
    def closeChrome(self, driver):
        try:
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                driver.close()
        except: pass
    def randomPictures(self, folderavt):
        if os.path.exists(folderavt) == False:
            return "NO_PATH_IMAGE"
        image = random.choice(os.listdir(folderavt))
        return image
    def loginGmail(self, driver, email, pwd_email):
        wait_20 = WebDriverWait(driver, 20)
        for _ in range(20):
            try:
                wait_20.until(EC.presence_of_element_located((By.XPATH, '//input[@type="email"]'))).send_keys(email)
                wait_20.until(EC.presence_of_element_located((By.ID, 'identifierNext'))).click()
                break
            except: sleep(2)
        for _ in range(20):
            try:
                wait_20.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))).send_keys(pwd_email)
                wait_20.until(EC.presence_of_element_located((By.ID, 'passwordNext'))).click()
                break
            except: sleep(2)
        sleep(5)
        try:
            wait_20.until(EC.presence_of_element_located((By.XPATH, '//input[@name="confirm"]'))).click()
        except: pass
    def selectBirthday(self, driver):
        wait_20 = WebDriverWait(driver, 20)
        try:
            listbox = wait_20.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@role="combobox"]')))
            listbox[0].click()
            month = random.randint(0,11)
            if month > 5:
                driver.execute_script('document.querySelector("#Month-options-list-container").scroll(0,100)')
            wait_20.until(EC.presence_of_element_located((By.XPATH, f'//div[@id="Month-options-item-{month}"]'))).click(); sleep(1)
            listbox[1].click()
            day = random.randint(0,27)
            scrollX = 0
            if day >= 6: scrollX = 200
            elif day >= 12: scrollX = 400 
            elif day >= 18: scrollX = 600 
            elif day >= 23: scrollX = 800 
            driver.execute_script(f'document.querySelector("#Day-options-list-container").scroll(0,{scrollX})')
            wait_20.until(EC.presence_of_element_located((By.XPATH, f'//div[@id="Day-options-item-{day}"]'))).click(); sleep(1)
            listbox[2].click()
            wait_20.until(EC.presence_of_element_located((By.XPATH, f'//div[text()="{random.randint(1985, 2003)}"]'))).click(); sleep(1)
            sleep(2)
            wait_20.until(EC.presence_of_element_located((By.XPATH, f'//button[@data-e2e="next-button"]'))).click()
            return True
        except:
            # tb = traceback.format_exc()
            # print(tb)
            for _ in range(10):
                if len(driver.find_elements(By.XPATH, value='//div[@role="combobox"]')) > 0:
                    return self.selectBirthday(driver)
                elif len(driver.find_elements(By.XPATH, value='//div[@role="combobox"]')) > 0:
                    return 'login_email'
                sleep(3)
            if len(driver.find_elements(By.XPATH, value='//a[@data-e2e="nav-profile"]')) > 0:
                return self.uploadAvatar(driver)
            return False
    def routeCaptcha(self, x, driver, type_cap, max_retries=10):
        retries = 0
        try:
            while retries < max_retries: 
                if type_cap == 0:
                    name_cap = ['outer', 'inner']
                    for name in name_cap:
                        image_element = driver.find_element_by_css_selector(f'[data-testid="whirl-{name}-img"]')
                        image_url = image_element.get_attribute('src')
                        if os.path.exists(f'img\\img_captcha\\{name}_image{x}.jpg'):
                            os.remove(f'img\\img_captcha\\{name}_image{x}.jpg')
                        image_name = f'{name}_image{x}.jpg'
                        urllib.request.urlretrieve(image_url, image_name)
                        save_directory = 'img\\img_captcha'
                        image_path = os.path.join(save_directory, image_name)
                        os.rename(image_name, image_path)
                
                solution = captchaTiktok(x, type_cap, self.API_KEY)

                # print(driver.title)
                draggable_button = driver.find_element(By.XPATH, '//div[@id="secsdk-captcha-drag-wrapper"]//div//div')
                actions = ActionChains(driver)
                actions.click_and_hold(draggable_button)
                # actions.move_by_offset(solution, 0)

                solu = int(solution)/5
                actions.move_by_offset(solu, 0).pause(0.5)
                actions.move_by_offset(solu, 0).pause(0.5)
                actions.move_by_offset(solu, 0).pause(0.5)
                actions.move_by_offset(solu, 0).pause(0.5)
                actions.move_by_offset(solu, 0) 
                actions.release()
                actions.perform()
                sleep(7)
                if len(driver.find_elements(By.XPATH, value='//img[@data-testid="whirl-outer-img"]')) == 0:
                    return True
                retries += 1
        except:
            return False
    def verifyImageCaptcha(self, x, driver):
        try:
            # solution = captchaTiktok(x, 2, self.API_KEY)
            # print(solution)
            solution = '465,258,272,92'
            # x1, y1, x2, y2 = 217, 162, 143, 257
            # x1, y1, x2, y2 = solution.split(',')
            # print(x1, y1, x2, y2)


            # element = driver.find_element(By.ID, value="captcha-verify-image")
            # actions = ActionChains(driver)
            # actions.move_to_element_with_offset(element, x1, y1).click().perform()
            # driver.implicitly_wait(1)
            # actions = ActionChains(driver)
            # actions.move_to_element_with_offset(element, x2, y2).click().perform()

            # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="captcha_container"]/div/div[3]/div[2]'))).click()


        except:
            return False
    def saveImageCaptcha(self, x, driver):
        image_element = driver.find_element_by_id('captcha-verify-image')
        image_url = image_element.get_attribute('src')
        if os.path.exists(f'img\\img_captcha\\verify_image{x}.jpg'):
            os.remove(f'img\\img_captcha\\verify_image{x}.jpg')
        image_name = f'verify_image{x}.jpg'
        urllib.request.urlretrieve(image_url, image_name)
        save_directory = 'img\\img_captcha'
        image_path = os.path.join(save_directory, image_name)
        os.rename(image_name, image_path)
    def completeAccount(self, driver):
        wait_20 = WebDriverWait(driver, 20)
        try:
            wait_20.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="loginContainer"]/div[3]/form/div[2]/div[3]/ul/li[{random.randint(1, 5)}]'))).click()
            sleep(3)
            wait_20.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="loginContainer"]/div[3]/form/button'))).click()
        except:
            for _ in range(10):
                if len(driver.find_elements(By.XPATH, value=f'//*[@id="loginContainer"]/div[3]/form/div[2]/div[3]/ul/li[{random.randint(1, 5)}]')) > 0:
                    return self.completeAccount(driver)
                if len(driver.find_elements(By.XPATH, value='//*[@id="loginContainer"]/div[3]/form/div[3]')) > 0:
                    wait_20.until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginContainer"]/div[3]/form/div[3]'))).click()
                    sleep(10)
                    return self.uploadAvatar(driver)
                sleep(3)
            return 'error_name'
        sleep(10)
        return self.uploadAvatar(driver)
    def uploadAvatar(self, driver):
        wait_20 = WebDriverWait(driver, 20)
        for _ in range(10):
            if len(driver.find_elements(By.XPATH, value='//a[@data-e2e="nav-profile"]')) > 0:
                href = driver.find_element(By.XPATH, '//a[@data-e2e="nav-profile"]').get_attribute('href')
                # print(href)
                if '@' in href and len(href.split('@')[1]) > 2: 
                    driver.get(href)
                    sleep(5)
                    if len(driver.find_elements(By.XPATH, '//div[@data-e2e="edit-profile-entrance"]//button')) > 0:
                        break
                    driver.refresh()
                else: 
                    driver.get('https://www.tiktok.com/')
                    sleep(3)
            driver.get('https://www.tiktok.com/')
            sleep(5)
        if '@' not in href or len(href.split('@')[1]) < 2:
            return 'error_link_user'
        try:
            user_tiktok = href.split('@')[1]
            wait_20.until(EC.presence_of_element_located((By.XPATH, '//div[@data-e2e="edit-profile-entrance"]//button'))).click(); sleep(2)

            image = self.randomPictures(self.path_image)
            wait_20.until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))).send_keys(f"{self.path_image}\\{image}")
            sleep(2)
            scroll_target = driver.find_element(By.XPATH, '//*[@id="tux-portal-container"]/div/div[2]/div/div/div[2]')
            driver.execute_script("arguments[0].scrollBy(0, 300);", scroll_target)
            sleep(2)
            wait_20.until(EC.presence_of_element_located((By.XPATH, '//div[@data-e2e="edit-profile-popup"]//div//div//button[2]'))).click(); sleep(2)
            wait_20.until(EC.presence_of_element_located((By.XPATH, '//button[@data-e2e="edit-profile-save"]'))).click()
            sleep(5)
            driver.refresh()
            sleep(5)
            return '@'+user_tiktok
        except:
            return 'error_upload'
    def mainReg(self, x, type_proxy, key_proxie):
        while True:
            self.lock.acquire()
            with open('data\\mail\\gmail.txt', 'r', encoding='utf-8') as file:
                email_remaining = file.readlines()
            # 
            if len(email_remaining) >= self.remaining:
                self.lock.release()
                print(f"{len(email_remaining)} : Đã đủ số lượng.", end='\r')
                # self.checkAndDelePro5()
                sleep(random.randint(50, 100))
                continue
            # 
            gmail = getMail()
            if list_email is False:
                return print("Đã hết email trong file")
            # 
            email = gmail.split('|')[0]
            pwd_email = gmail.split('|')[1].strip()
            self.lock.release()
            # 
            if type(key_proxie) != list:
                while True:
                    print(f"Thread: {x}: Email: {email} >> Đang lấy proxy", end='\r')
                    if type_proxy == 1:
                        proxie = self.api_proxie.DTProxy(key_proxie)
                    elif type_proxy == 2:
                        key = key_proxie.split('|')[0]
                        proxie = key_proxie.split('|')[1]
                        change = self.api_proxie.ChangeProxyNo1(key)
                        if change == False:
                            sleep(10)
                            continue
                        sleep(10)
                    elif type_proxy == 3:
                        proxie = self.api_proxie.ChangeProxyTinsoft(key_proxie)
                    elif type_proxy == 4:
                        proxie = self.api_proxie.Wwproxy(key_proxie)
                        sleep(5)
                    if proxie != False and proxie != None:
                        if len(proxie.split(':')) > 2:
                            splitProxy = proxie.split(':')
                            host = splitProxy[0]
                            port = splitProxy[1]
                            user = splitProxy[2]
                            pwd = splitProxy[3]
                            proxie_rq = f'{user}:{pwd}@{host}:{port}'
                        else:
                            proxie_rq = proxie
                        proxie_rq = {'https': 'http://'+proxie_rq}
                        try: 
                            ip = requests.get('https://api.myip.com', proxies=proxie_rq).text
                            break
                        except: pass
                    sleep(5)
            else:
                proxie = random.choice(key_proxie).strip()
            
            self.regAccount(x, email, pwd_email, proxie)

    def regAccount(self, x, email, pwd_email, proxie='null'):
        print(f"Thread: {x}: Email: {email} >> Tiến hành mở trình duyệt", end='\r')
        profile_id = self.gpm.GPM_CreateProfilev3(proxie, group='test')['id']
        driver = self.setupChrome(profile_id, x, 0.5, 7)
        if driver == 'Exception':
            return print("Lỗi không mong muốn khi mở chrome")
        elif driver == 'loading':
            return print("Vui lòng tắt profile cũ trước khi chạy cùng 1 profile")
        try:
            driver.get('https://accounts.google.com/')
            self.loginGmail(driver, email, pwd_email)
            sleep(5)
            driver.get('https://www.tiktok.com/')
            sleep(10)
            for _ in range(10):
                try: WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/tiktok-cookie-banner//div/div[2]/button[2]'))).click()
                except: pass
                try: WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'header-login-button'))).click()
                except: pass
                try: WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@data-e2e="see-more-btn"]'))).click()
                except: pass
                try:
                    eles = driver.find_elements(By.XPATH, value='//div[@data-e2e="channel-item"]')
                    if len(eles) > 2:
                        break
                except: 
                    driver.get('https://www.tiktok.com/')
                    sleep(5)
            for ele in eles:
                text = ele.get_attribute("outerHTML")
                if 'Google' in text:
                    ele.click()
                    break

            sleep(10)
            driver.switch_to.window(driver.window_handles[1])
            # login gmail
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, f"//div[text()='{email}']"))).click()
            sleep(7)
            
            # cho phép quyền truy cập
            try: 
                if len(driver.find_elements(By.XPATH, value='//div[@role="presentation"]//div/div[2]/div/div[2]/div/div/div[2]/div/div/button')) > 0:
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//div[@role="presentation"]//div/div[2]/div/div[2]/div/div/div[2]/div/div/button'))).click()
            except: pass
            
            sleep(5)
            driver.switch_to.window(driver.window_handles[0])
            
            if len(driver.find_elements(By.XPATH, value='//img[@data-testid="whirl-outer-img"]')) > 0:
                bypass = self.routeCaptcha(x, driver, type_cap=0)
            elif len(driver.find_elements(By.XPATH, value='//img[@class="captcha_verify_img_slide"]')) > 0:
                self.saveImageCaptcha(x, driver)
                bypass = self.routeCaptcha(x, driver, type_cap=1)
            elif len(driver.find_elements(By.ID, value='captcha-verify-image')) > 0 and len(driver.find_elements(By.XPATH, value='//img[@class="captcha_verify_img_slide"]')) == 0:
                self.saveImageCaptcha(x, driver)
                bypass = self.verifyImageCaptcha(x, driver)
            
            birthday = self.selectBirthday(driver)
            if birthday != False:
                if birthday == True:
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    print(f"[{current_time}] : Thread: {x}: Email: {email} : IP: {proxie} : >> Đang giải captcha ...", end='\r')
                    sleep(5)
                    for _ in range(5):
                        bypass = False
                        if len(driver.find_elements(By.XPATH, value='//img[@data-testid="whirl-outer-img"]')) > 0:
                            bypass = self.routeCaptcha(x, driver, type_cap=0)
                        elif len(driver.find_elements(By.XPATH, value='//img[@class="captcha_verify_img_slide"]')) > 0:
                            self.saveImageCaptcha(x, driver)
                            bypass = self.routeCaptcha(x, driver, type_cap=1)
                        elif len(driver.find_elements(By.ID, value='captcha-verify-image')) > 0 and len(driver.find_elements(By.XPATH, value='//img[@class="captcha_verify_img_slide"]')) == 0:
                            self.saveImageCaptcha(x, driver)
                            bypass = self.verifyImageCaptcha(x, driver)
                        else:
                            sleep(5)
                            continue
                        break
                else: bypass = True

                if bypass != False:
                    sleep(5)
                    if birthday == True:
                        complete = self.completeAccount(driver)
                    else:
                        complete = birthday
                    if complete == 'error_name':
                        noti_done = "Set name error"
                    elif complete == 'error_upload':
                        noti_done = "Avatar upload failed"
                    elif complete == 'error_link_user':
                        noti_done = "Can't get user link"
                    else:
                        now = datetime.now()
                        current_time = now.strftime("%H:%M:%S")
                        username_tiktok = complete.replace('@', '')
                        noti_done = 'Create account success'

                        print(f"[{current_time}] : Thread: {x}: Email: {email} : IP: {proxie} >> {noti_done}")
                        data_post = f"{email}|{pwd_email}|{username_tiktok}"
                        postMail(data_post)

                        self.closeChrome(driver)
                        self.gpm.GPM_DeleteProfilev3(profile_id)
                        return True
                    noti_fail = complete
                else:
                    noti_fail = 'Bypass captcha failed'
                
            elif birthday == 'login_email':
                if len(driver.find_elements(By.XPATH, value='/html/body/tiktok-cookie-banner//div/div[2]/button[2]')) > 0:
                    driver.refresh()
                    self.closeChrome(driver)
                    self.gpm.GPM_DeleteProfilev3(profile_id)
                    # 
                    print(f"Thread: {x}: Email: {email} : IP: {proxie} >> Đang tiến hành đăng ký lại tài khoản", end='\r')
                    return self.regAccount(x, email, pwd_email, proxie)
            else:
                noti_fail = 'Select birthday failed'
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(f"[{current_time}] : Thread: {x}: Email: {email} : IP: {proxie} >> {noti_fail}")
            with open('reg\\reg_fail.txt', 'a+', encoding='utf-8') as file:
                file.write(f"{email}|{pwd_email}|{noti_fail}\n")
            # 
            self.closeChrome(driver)
            self.gpm.GPM_DeleteProfilev3(profile_id)
            return False
        except Exception as e:
            err = repr(e)
            print(f"Thread: {x}: Email: {email} : IP: {proxie} >> {err}")
            with open('reg\\reg_fail.txt', 'a+', encoding='utf-8') as file:
                file.write(f"{email}|{pwd_email}|{err}\n")
            # 
            self.closeChrome(driver)
            self.gpm.GPM_DeleteProfilev3(profile_id)
            return False
    
    def test(self, x, email, pwd_email):
        driver = self.setupChrome('profile_id', 0, 0.5, 8)
        if len(driver.find_elements(By.ID, value='captcha-verify-image')) > 0 and len(driver.find_elements(By.XPATH, value='//img[@class="captcha_verify_img_slide"]')) == 0:
            # self.saveImageCaptcha(x, driver)
            bypass = self.verifyImageCaptcha(x, driver)


proxy_key = True
with open('data\\proxy\\api_key.json', 'r', encoding='utf-8-sig') as file:
    file_key = json.loads(file.read())

type_proxy = int(input("[1] : Dtproxy\n[2] : Proxyno1\n[3] : Tinsoft\n[4] : Wwproxy\n[0] : Dùng proxy tĩnh\nChọn: "))
if type_proxy == 1:
    threads = len(file_key['keydt']) # thread theo số lượng key proxy
elif type_proxy == 2:
    threads = len(file_key['keyno1']) # thread theo số lượng key proxy
elif type_proxy == 3:
    threads = len(file_key['key_tinsoft']) # thread theo số lượng key proxy
elif type_proxy == 4:
    threads = len(file_key['key_wwproxy']) # thread theo số lượng key proxy
else:
    threads = 0

if threads <= 0:
    proxy_key = False
    print("[*] : Đối với chạy proxy random vui lòng nhập dãy proxy vào file proxy_reg theo định dạng IP:HOST:USER:PASS")
    threads = int(input("Nhập số luồng: "))


for x in range(threads):
    if type_proxy == 1:
        proxie = file_key['keydt'][x]
    elif type_proxy == 2:
        proxie = file_key['keyno1'][x]
    elif type_proxy == 3:
        proxie = file_key['key_tinsoft'][x]
    elif type_proxy == 4:
        proxie = file_key['key_wwproxy'][x]
    else:
        with open('data\\proxy\\proxy_reg.txt', 'r', encoding='utf-8') as file:
            proxie = file.readlines()
    Thread(target=RegTiktok().mainReg, args=(x, type_proxy, proxie, )).start()
    sleep(2)

# email = 'dangchinhchinh239@thptquydon.com'
# pwd_email = 'danh9999@'
# x = 0
# RegTiktok().test(x, email, pwd_email)