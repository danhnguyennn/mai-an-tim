import time
import cv2
import string
import random
import traceback
import os
import numpy as np
from lxml import html
from time import sleep
from ppadb.client import Client as AdbClient

def randStr(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
class ADB_TOOL:
    def __init__(self, adbs) -> None:
        adb = AdbClient(host="127.0.0.1", port=5037)
        self.adbs = adbs
        self.device = adb.device(serial=adbs)
    
    def runShell(self, command, type='shell', xml='file.xml', check=False):
        for i in range(10):
            try:
                if type == 'shell':
                    return self.device.shell(command)
                elif type == 'pull':
                    return self.device.pull(command, xml)
                elif type == 'screencap':
                    return self.device.screencap()
            except:
                if check == True: return False
                time.sleep(5)
                print(command, "Lỗi mất kết nối usb")
        return False
    def checkVerisonAndroid(self):
        result = self.runShell("getprop ro.build.version.release")
        return result.strip()
    def clicks(self, click_x, click_y, time=1):
        for _ in range(time):
            self.runShell(f"input tap {click_x} {click_y}")
    def doubleClick(self, click_x, click_y):
        self.runShell(f"input tap {click_x} {click_y} & sleep 0.1; input tap {click_x} {click_y}")
    def find_image(self, small_image_path, loop=2, click=True, double=False, cord=False, screenshot=True, threshold=0.55, row=''):
        for i in range(loop):
            try:
                # Đọc và lấy kích thước ảnh nhỏ
                small_image = cv2.imread(small_image_path)
                small_height, small_width, _ = small_image.shape
                for _ in range(loop):
                    result = self.runShell('', type='screencap')
                    nparr = np.frombuffer(result, np.uint8)
                    large_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    # Thực hiện template matching 
                    result = cv2.matchTemplate(large_image, small_image, cv2.TM_CCOEFF_NORMED)
                    # Tìm vị trí tối đa của sự trùng khớp
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    # Nếu trùng khớp đạt đến một ngưỡng nhất định, vẽ hình chữ nhật
                    # print(max_val)
                    if max_val >= threshold:
                        top_left = max_loc
                        bottom_right = (top_left[0] + small_width, top_left[1] + small_height)
                        # Tính toán tọa độ tâm của hình chữ nhật
                        center_x = (top_left[0] + bottom_right[0]) // 2
                        center_y = (top_left[1] + bottom_right[1]) // 2
                        if click:
                            click_x = center_x  # Đặt tọa độ x cho việc nhấp vào
                            click_y = center_y  # Đặt tọa độ y cho việc nhấp vào
                            if double:
                                self.runShell(f"input tap {click_x} {click_y} & sleep 0.1; input tap {click_x} {click_y}")
                            else:
                                self.runShell(f"input tap {click_x} {click_y}")
                        if cord == True:
                            return {'x1':top_left[0], 'y1':top_left[1], 'x2':bottom_right[0], 'y2':bottom_right[1]}
                        return True
                    else:
                        if loop != 1:
                            time.sleep(1)
                return False
            except Exception as e:
                tb = traceback.format_exc()
                print(tb)
                time.sleep(5)
        return False
    def send_keys(self, text):
        self.runShell(f"input text {text}")
    def getvmSize(self):
        size = self.runShell(f"wm size").split(': ')[1].strip().split('x')
        return size
    def checkColor(self):
        try:
            result = self.runShell('', type='screencap')
            nparr = np.frombuffer(result, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            average_pixel_value = np.mean(gray_image)
            print(average_pixel_value)
            if average_pixel_value < 10:
                return False
            else:
                return True
        except:
            return False    
    def dumXml(self):
        self.runShell("uiautomator dump")
        self.runShell(f"/sdcard/window_dump.xml", "pull", f"xml/{self.adbs}.xml")
        return f'xml/{self.adbs}.xml'
    def getPosXml(self, element):
        pos = []
        try:
            tree = html.parse(self.dumXml())
            for bound in tree.xpath(element):
                gg = bound.attrib['bounds'].split('][')[0].replace('[', '').split(',')
                pos.append([int(gg[0]), int(gg[1])])
            return pos
        except:
            return pos
    def checkXml(self, CountRepeat=15, element=None, index=0, posList=False, click=True, Xoffsetplus=0, Yoffsetplus=0):
        for i in range(CountRepeat):
            pos = self.getPosXml(element)
            # print(pos)
            if pos != []:
                if click == True:
                    pos = pos[index]
                    self.clicks(pos[0]+Xoffsetplus, pos[1]+Yoffsetplus)    
                    # print("Đã click", element)
                if posList == True:
                    return pos
                return True
        return False
    def FindElement(self, element, index, attribute):
        try:
            tree = html.parse(f"xml/{self.adbs}.xml").xpath(element)[index].attrib[attribute]
            return tree
        except:
            return False
    
# adb = ADB_TOOL('420073a5d0d6b42f')

def startTiktok():
    adb.checkXml(CountRepeat=5, element='//node[@text="Bỏ qua"]')
    adb.checkXml(CountRepeat=5, element='//node[@text="Bắt đầu xem"]')
    adb.runShell("input swipe 224 1435 143 285 100")
    for _ in range(15):
        if adb.checkXml(CountRepeat=1, element='//node[@content-desc="Hồ sơ"]'): break
        adb.runShell("input swipe 224 1435 143 285 100")
def registerTiktok():
    adb.checkXml(element='//node[@content-desc="Tiếp tục với Google"]')
    adb.checkXml(element='//node[@resource-id="com.google.android.gms:id/account_name"]')
    if adb.checkXml(CountRepeat=20, element='//node[@text="Ngày sinh"]'):
        adb.runShell(f"input swipe 266 1663 283 1263 {random.randint(900,1100)}")
        adb.runShell(f"input swipe 536 1650 550 1296 {random.randint(900,1100)}")
        adb.runShell(f"input swipe 803 1383 813 1881 {random.randint(90,130)}") # Năm Sinh
        adb.runShell(f"input swipe 803 1383 813 1881 {random.randint(100,120)}") # Năm Sinh
        adb.runShell(f"input swipe 803 1383 813 1881 {random.randint(200,300)}") # Năm Sinh
        adb.runShell(f"input swipe 803 1383 813 1881 {random.randint(200,400)}") # Năm Sinh

        xml_file = f"{adb.adbs}.xml"
        adb.checkXml(element='//node[@text="Tiếp"]', xml=xml_file)
        adb.checkXml(element='//node[@text="Xác nhận"]')
        for _ in range(5):
            if adb.checkXml(CountRepeat=1, element='//node[@content-desc="Hồ sơ"]') == False:
                adb.checkXml(element='//node[@text="TỪ CHỐI"]')
def upAvatar():
    folder_avater = 'F:\\images'
    # adb.runShell('pm grant com.ss.android.ugc.trill android.permission.WRITE_EXTERNAL_STORAGE')
    # imgs = adb.runShell('rm -r /sdcard/Pictures/*')
    # img_name = randomPictures(folder_avater)
    # print(img_name)
    # adb.device.push(folder_avater+'/'+img_name, '/sdcard/Pictures/0.jpg')
    # adb.runShell('am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/Pictures/0.jpg')
    
    # adb.find_image('img\\suahoso.png', 2)
    # adb.checkXml(element='//node[@text="Thay đổi ảnh"]', Xoffsetplus=100, Yoffsetplus=-100)
    # adb.find_image('img\\chontuthuvien.png', 5)
    posList = adb.checkXml(CountRepeat=1, element='//node[@class="android.widget.ImageView"]', click=False, posList=True)
    print("len", len(posList))
    for _ in range(len(posList)):
        pos = posList[_]
        print(pos)
        adb.clicks(int(pos[0]), int(pos[1]))
        sleep(2)
        black = adb.checkColor()
        if black: break
        adb.runShell("input keyevent 4")
    adb.find_image('img\\choose_img.png', 2)
    adb.checkXml(CountRepeat=1, element='//node[@text="Xác nhận"]')
    up = True
    for _ in range(2):
        if adb.checkXml(CountRepeat=2, element='//node[@text="Lưu & đăng" or @text="Lưu"]') == False: 
            up = False
            break
        sleep(5)
    if adb.checkXml(CountRepeat=20, element='//node[@text="Thay đổi ảnh"]', click=False):
        adb.runShell("input keyevent 4")
        if up == False:
            return upAvatar(folder_avater)
    else:
        adb.runShell("input keyevent 4")
        adb.runShell("input keyevent 4")
    return True
def randomPictures(folderavt):
    if os.path.exists(folderavt) == False:
        return "NO_PATH_IMAGE"
    image = random.choice(os.listdir(folderavt))
    return image
def getUsername():
    adb.runShell("input swipe 588 300 577 1600 100") # vuốt lên đầu
    for _ in range(15):
        if adb.checkXml(CountRepeat=1, element='//node[@content-desc="Hồ sơ"]'): break
        adb.runShell("input swipe 224 1435 143 285 100")
    adb.runShell("input swipe 588 300 577 1600 100") # vuốt lên đầu
    root = html.parse(adb.dumXml())
    elements = root.findall(".//*[@resource-id]")
    for element in elements:
        if '@' in element.attrib['text']:
            username=element.attrib['text'].replace("@", "")
            print(username)

