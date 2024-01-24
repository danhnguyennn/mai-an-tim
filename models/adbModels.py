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
                print(self.adbs, command, "Lỗi mất kết nối usb")
        return False
    def checkVerisonAndroid(self):
        result = self.runShell("getprop ro.build.version.release")
        return result.strip()
    def clicks(self, click_x, click_y, time=1):
        for _ in range(time):
            self.runShell(f"input tap {click_x} {click_y}")
    def doubleClick(self, click_x, click_y):
        self.runShell(f"input tap {click_x} {click_y} & sleep 0.1; input tap {click_x} {click_y}")
    def find_image(self, small_image_path, loop=2, click=True, double=False, cord=False, screenshot=True, threshold=0.55, row='', print_text=False):
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
                    if print_text:
                        print(max_val)
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
                    # else:
                    #     if loop != 1:
                    #         time.sleep(0.5)
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
            # print(average_pixel_value)
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
    