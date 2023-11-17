import os
import sys
import json
import random
import string
import requests
import threading
import traceback

from datetime import *
from time import sleep

import numpy as np
from lxml import html
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from threading import Thread, Event
from PyQt5.QtWidgets import *
import xml.etree.ElementTree as ET
import data.display_ui.icons.img_rc as img_rc
from PyQt5 import QtCore, QtGui, QtWidgets, uic
# ui
from data.display_py.main import Ui_MainWindow
# model
from models.tdsModel import API_TDS
from models.adbModels import ADB_TOOL
from models.mongoServer import MONGO_DB
from models.captcha import bypassCaptcha

VERSION = '1.1.1.4'

def Information(content):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(content)
    msg.setWindowTitle("Thông Báo")
    msg.setWindowIcon(QtGui.QIcon('data\\display_ui\\icons\\infomation.png'))
    msg.exec_()
def my_excepthook(exctype, value, traceback):
    Information(f"MAIN: VALUE > {value} : exctype > {exctype} : traceback > {traceback}")
def getCurrentTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    today = now.strftime("%d-%m-%Y")
    return {
        'time': current_time,
        'day' : today
    }
def randStr(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()

        # self.uic = uic.loadUi('data\\display_ui\\main.ui', self)
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self)
        # 
        self.last_pos = QPoint()
        # REMOVE TITLE BAR
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.uic.topVersionApp.setText(f'Version: {VERSION}')
        self.uic.taskbar_version.setText(VERSION)
        self.runFirst()

        # tasbar
        self.uic.taskbar_active.setText('Trạng thái : active')
        self.uic.taskbar_device.setText('Thiết bị : Win***')
        # button
        self.uic.btn_close.clicked.connect(self.eventClose)
        self.uic.btn_max.clicked.connect(self.minimizeEvent)
        self.uic.btn_mini.clicked.connect(lambda: self.showMinimized())
        self.uic.btn_menu.clicked.connect(self.showMenu)
        # self.uic.btn_home.clicked.connect(self.showHome)
        self.uic.btn_show.clicked.connect(self.showColumnTable)
        self.uic.btn_history.clicked.connect(self.showHistory)
        self.uic.btn_cauhinh.clicked.connect(self.showCauHinhTool)
        self.uic.btn_showC.clicked.connect(self.showFarmExtra)
        self.uic.btn_add_account.clicked.connect(self.showAddAccount)
        self.uic.btn_savecmd.clicked.connect(self.clickedSaveSetting)

        self.uic.btn_batdau.clicked.connect(self.__startMultiThread)
        self.uic.btn_dunglai.clicked.connect(self.__stopMultiThread)

        self.uic.tablewidget_page.setContextMenuPolicy(Qt.CustomContextMenu)
        self.uic.tablewidget_page.customContextMenuRequested.connect(self.contextMenuEvent)

    def runFirst(self):
        self.updateDay = False
        self.list_task = ['Chọn', 'STT', 'idObject', 'Session', 'Phone', 'Device', 'Verison', 'Tiktok', 'Username', 'Password', 'Total', 'Xu Hnay', 'VPN', 'Cache', 'Thao tác','Trạng thái','Lần chạy cuối']
        with open('config\\config.json', 'r', encoding='utf-8-sig') as file:
            config = json.loads(file.read())
            self.stoLocation = config['StoLocation']
            self.dayrun = config['day']
        today = self.dayrun.split('-')
        current_time = getCurrentTime()['day']
        dayVn = current_time.split('-')
        if date(int(today[2]), int(today[1]), int(today[0])) < date(int(dayVn[2]), int(dayVn[1]), int(dayVn[0])):
            config['day'] = current_time
            with open('config\\config.json', 'w') as config_file:
                json.dump(config, config_file, indent=4)
            self.updateDay = True
        if self.stoLocation == 'mongodb':
            self.db = MONGO_DB()
        elif self.stoLocation == 'sqlite':
            pass
        # load setting
        self.loadDataSetting()
        self.setSetting()
        self.loadSettingShow()
        self.threadStartChrome = {}
        self.threadExtension = {}
        self.listThreadRunning = []
        self.eventTitleBar = 0
        self.count_checked = 0
        # table
        self.setDefautTable()

    # event display
    def contextMenuEvent(self, event):
        self.menu = QMenu()
        # action 1
        actionClickBox = QMenu("Chọn", self)
        actionClickBox.setIcon(QIcon('data/display_ui/icons/checkBox.png'))

        boxAll = QAction("Tất cả", self)
        boxAll.setIcon(QIcon('data/display_ui/icons/todo_list_25px.png'))
        boxFocus = QAction("Bôi đen", self)
        boxFocus.setIcon(QIcon('data/display_ui/icons/boiden.png'))
        boxCurrent = QAction("Hàng hiện tại", self)
        boxCurrent.setIcon(QIcon('data/display_ui/icons/current_tick.png'))

        actionClickBox.addAction(boxAll)
        actionClickBox.addAction(boxFocus)
        actionClickBox.addAction(boxCurrent)
        # action 2
        actionCancelBox = QAction("Bỏ chọn tất cả", self)
        actionCancelBox.setIcon(QIcon('data/display_ui/icons/cancelBox.png'))
        # action 3
        actionDele = QAction("Xóa tài khoản", self)
        actionDele.setIcon(QIcon('data/display_ui/icons/delete.png'))
        # action 4

        # action 5
        actionCopy = QMenu("Copy", self)
        actionCopy.setIcon(QIcon('data/display_ui/icons/copy.png'))

        copyUsername = QAction("Username", self)
        # copyUsername.setIcon(QIcon('data/display_ui/icons/gmail.png'))
        copyPassword = QAction("Password", self)
        # copyPassword.setIcon(QIcon('data/display_ui/icons/password_gmail.png'))
        copyDevice = QAction("Device", self)
        # copyDevice.setIcon(QIcon('data/display_ui/icons/recovery_gmail.png'))
        copyAll = QAction("Device|Username|Password|Xu", self)
        # copyAll.setIcon(QIcon('data/display_ui/icons/recovery_gmail.png'))

        
        actionCopy.addAction(copyDevice)
        actionCopy.addAction(copyUsername)
        actionCopy.addAction(copyPassword)
        actionCopy.addAction(copyAll)

        # action 6
        actionCheck = QAction("Kiểm tra xu tất cả", self)
        actionCheck.setIcon(QIcon('data/display_ui/icons/money.png'))

        actionSend = QAction("Chuyển xu", self)
        actionSend.setIcon(QIcon('data/display_ui/icons/profits.png'))

        actionChangePwd = QAction("Thay đổi mật khẩu", self)
        actionChangePwd.setIcon(QIcon('data/display_ui/icons/reset-password.png'))

        # action 7
        actionUpdate = QAction("Cập nhật dữ liệu", self)
        actionUpdate.setIcon(QIcon('data/display_ui/icons/update.png'))
        
        actionReset = QAction("Reset session máy", self)
        actionReset.setIcon(QIcon('data/display_ui/icons/restart.png'))

        # action 8
        actionLoad = QAction("Tải lại danh sách", self)
        actionLoad.setIcon(QIcon('data/display_ui/icons/load.png'))

        row = ''
        for position in self.uic.tablewidget_page.selectedItems():
            row = position.row()
        if str(row).isnumeric():
            self.menu.popup(QCursor.pos())

        self.menu.addMenu(actionClickBox)
        self.menu.addAction(actionCancelBox)
        self.menu.addMenu(actionCopy)
        self.menu.addAction(actionCheck)
        self.menu.addAction(actionSend)
        self.menu.addAction(actionChangePwd)
        self.menu.addAction(actionUpdate)
        self.menu.addAction(actionDele)
        self.menu.addAction(actionReset)
        self.menu.addAction(actionLoad)

        # menu con
        boxAll.triggered.connect(self.selectAllCheckbox)
        boxFocus.triggered.connect(self.selectCheckboxFocus)
        boxCurrent.triggered.connect(self.selectCurrentBox)
        actionCancelBox.triggered.connect(self.unAllCheckbox)
        actionDele.triggered.connect(self.deleAccount)
        actionReset.triggered.connect(self.resetSession)
        actionLoad.triggered.connect(lambda: self.loadData(True))

        actionUpdate.triggered.connect(self.updateDataAccount)
        actionCheck.triggered.connect(self.__checkXuAll)
        actionSend.triggered.connect(self.__sendXu)
        actionChangePwd.triggered.connect(self.__changePwdTds)
    def eventClose(self):
        self.close()
    def minimizeEvent(self):
        if self.eventTitleBar == 0:
            self.showMaximized()
            self.eventTitleBar = 1
        else:
            self.showNormal()
            self.eventTitleBar = 0
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startPos = event.pos()
    def mouseMoveEvent(self, event):
        if self.startPos:
            self.move(self.pos() + (event.pos() - self.startPos))
    
    # event
    def selectAllCheckbox(self):
        count = self.uic.tablewidget_page.rowCount()
        for i in range(count):
            item = self.uic.tablewidget_page.item(i, 0)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setCheckState(Qt.Checked)
        self.uic.taskbar_dachon.setText(f"Đã chọn: {str(count)}")
    def selectCheckboxFocus(self):
        for i in self.userSelectedCheckboxList:
            item = self.uic.tablewidget_page.item(i, 0)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setCheckState(Qt.Checked)
    def selectCurrentBox(self):
        item = self.uic.tablewidget_page.item(self.row, 0)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        item.setCheckState(Qt.Checked)
    def unAllCheckbox(self):
        for i in range(self.uic.tablewidget_page.rowCount()):
            item = self.uic.tablewidget_page.item(i, 0)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setCheckState(Qt.Unchecked)
    def deleAccount(self):
        dele_success = 0
        account_dele = []
        for i in range(self.uic.tablewidget_page.rowCount()):
            isCheck = self.uic.tablewidget_page.item(i, 0).checkState()
            if isCheck == 2: # 2 check được chọn 0 là chưa được chọn
                idObject = self.uic.tablewidget_page.item(i, 2).text()
                account_dele.append(idObject)
        # messbox
        if len(account_dele) == 0: return
        mess = QMessageBox()
        mess.setWindowTitle('Xóa tài khoản')
        mess.setWindowIcon(QtGui.QIcon('data\\display_ui\\icons\\infomation.png'))
        mess.setText(f'''Bạn có muốn xóa {len(account_dele)} tài khoản đã chọn ? \n\nTài khoản đã xóa hiện không thể khôi phục !!!''')
        mess.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        x = mess.exec()
        if x == QMessageBox.StandardButton.Yes:
            for idObject in account_dele:
                delete = self.db.deleteAccount(idObject)
                if delete:
                    dele_success += 1
            Information(f"Xóa thành công {dele_success} tài khoản")
        self.loadData()
    def addAccountDB(self):
        print(self.arr_account_add)
        succ = 0
        fail = 0
        for i, text in enumerate(self.arr_account_add):
            try:
                acc_t = text.split('|')
                device = acc_t[0]
                usertds = acc_t[1]
                passtds = acc_t[2]
                dict_account = {
                    'session': 'FAIL',
                    'phone': 'Máy xx',
                    'device': device,
                    'version': '',
                    'user_tiktok': '',
                    'usertds': usertds,
                    'pwdtds': passtds,
                    'xu': '0',
                    'xuhnay': '0',
                    'vpn': '1111'
                }
                self.db.addAccount(dict_account)
                succ += 1
            except:
                fail += 1
        self.uic.add_success.setText(f"Thành công: {succ}")
        self.uic.add_fail.setText(f"Thất bại: {fail}")
        Information(f"Thêm thành công {succ} tài khoản")
        self.loadData()

    # setting
    def saveSetting(self):
        radioTaphoa = self.uic.radioTaphoa.isChecked()
        radioFile = self.uic.radioFile.isChecked()
        token_taphoa = self.uic.token_taphoa.text()
        token_shop = self.uic.token_shop.text()
        textGmail = self.uic.textGmail.toPlainText()
        apikey1st = self.uic.key_captcha.text()
        dl_min = self.uic.delayMin.text()
        dl_max = self.uic.delayMax.text()
        path_image = self.uic.path_image.text()
        limit_xu = self.uic.limitXu.text()
        sleep_job = self.uic.sleep_job.text()
        job_sleep = self.uic.job_sleep.text()

        if radioTaphoa:
            getMail = 'api'
        elif radioFile:
            getMail = 'file'
            with open('data\\mail\\gmail.txt', 'w', encoding='utf-8') as save:
                save.write(textGmail)
            self.mailDistribution()
            self.uic.textGmail.clear()
        dict_setting = {
            'getMail': getMail, # file
            'site': 'taphoammo',
            'apiKeyTaphoa': token_taphoa,
            'keyShop': token_shop,
            'apikey1st': apikey1st,
            'dlMin': dl_min,
            'dlMax': dl_max,
            'path_image': path_image,
            'limitXu': limit_xu,
            'stopSleep': sleep_job,
            'limitStopAcc': job_sleep
        }
        
        self.db.updateSetting(dict_setting)
        self.loadDataSetting()
        Information("Đã lưu cài đặt")
    def loadDataSetting(self):
        dict_setting        = self.db.getSetting()
        self.dict_setting   = dict_setting
        self.getMail        = dict_setting['getMail']
        self.site           = dict_setting['site']
        self.apiKeyTaphoa   = dict_setting['apiKeyTaphoa']
        self.keyShop        = dict_setting['keyShop']
        self.apikey1st      = dict_setting['apikey1st']
        self.dlMin          = dict_setting['dlMin']
        self.dlMax          = dict_setting['dlMax']
        self.path_image     = dict_setting['path_image']
        self.limitXu        = dict_setting['limitXu']
        self.stopSleep      = dict_setting['stopSleep']
        self.limitStopAcc   = dict_setting['limitStopAcc']
    def setSetting(self):
        if self.getMail == 'api':
            self.uic.radioTaphoa.setChecked(True)
        elif self.getMail == 'file':
            self.uic.radioFile.setChecked(True)
        self.uic.token_taphoa.setText(self.apiKeyTaphoa)
        self.uic.token_shop.setText(self.keyShop)
        self.uic.key_captcha.setText(self.apikey1st)
        self.uic.delayMin.setValue(int(self.dlMin))
        self.uic.delayMax.setValue(int(self.dlMax))
        self.uic.path_image.setText(self.path_image)
        self.uic.limitXu.setText(self.limitXu)
        self.uic.sleep_job.setValue(int(self.stopSleep))
        self.uic.job_sleep.setValue(int(self.limitStopAcc))
        
    # extension
    def resetSession(self):
        x = 0
        for row in range(self.uic.tablewidget_page.rowCount()):
            isCheck = self.uic.tablewidget_page.item(row, 0).checkState()
            if isCheck == 2: # 2 check được chọn 0 là chưa được chọn
                object_id = self.uic.tablewidget_page.item(row, 2).text()
                self.db.updateOneAccount(object_id, {
                    'session': 'FAIL',
                    'user_tiktok': '',
                    })
                self.setColorStatusTable(row, 3, 'FAIL')
                x += 1
        if x == 0:
            return Information("Vui lòng chọn tài khoản cần xóa dữ liệu.")
        Information(f"Xóa thành công dữ liệu của {x} tài khoản.")
    def mailDistribution(self):
        try:
            base_directory = os.getcwd()
            input_file = 'data\\mail\\gmail.txt'
            for i in range(self.count):
                target_directory = os.path.join(base_directory, str(i), 'data', 'gmail.txt')
                if os.path.exists(target_directory):
                    open(target_directory, 'w').close()

            with open(base_directory+'\\'+input_file, 'r') as f:
                emails = f.readlines()
            emails = [email.strip() for email in emails]

            for i, email in enumerate(emails):
                target_directory = os.path.join(base_directory, 'data', 'mail', 'stream', str((i % self.count) + 1))
                if not os.path.exists(target_directory):
                    os.makedirs(target_directory)
                with open(target_directory+'\\gmail.txt', 'a') as f:
                    f.write(email + '\n')
                with open(target_directory+'\\gmail_done.txt', 'a') as f:
                    pass
            return True
        except:
            return False
    def updateDataAccount(self):
        list_object = []
        list_row = []
        x = 0
        for row in range(self.uic.tablewidget_page.rowCount()):
            isCheck = self.uic.tablewidget_page.item(row, 0).checkState()
            if isCheck == 2: # 2 check được chọn 0 là chưa được chọn
                object_id = self.uic.tablewidget_page.item(row, 2).text()
                list_object.append(object_id)
                list_row.append(row)
                x += 1
        if x == 0:
            return Information("Vui lòng chọn tài khoản cần cập nhật.")
        dlg = updateData(self.uic, list_row, list_object)
        dlg.exec_()

    # setitng show column table
    def setDefautTable(self):
        self.uic.btn_dunglai.setEnabled(False)
        checkbox_style = CheckBoxStyle()
        self.uic.tablewidget_page.setStyle(checkbox_style)
        self.uic.tablewidget_page.cellChanged.connect(self.onCellChange)
        self.uic.tablewidget_page.selectionModel().selectionChanged.connect(self.GetXY)
        self.uic.tablewidget_page.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.uic.tablewidget_page.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.uic.tablewidget_page.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.uic.tablewidget_page.setHorizontalHeaderLabels(self.list_task)
        self.setSizeColumn()
        self.loadData()
    def loadData(self, noti=False):
        Account = self.db.getAllAccount()
        list_account = Account['data']
        self.count = Account['count']
        combo_items = ['1111', 'hma', 'ssmax']

        self.uic.stackedWidget.setCurrentWidget(self.uic.page_showPage)
        self.uic.tablewidget_page.setColumnCount(len(self.list_task))
        self.uic.tablewidget_page.setRowCount(self.count)
        j = 1
        for data in list_account:
            item = QTableWidgetItem(str(j))
            item.setForeground(QColor(84, 110, 122))
            item.setTextAlignment(Qt.AlignCenter)
            self.uic.tablewidget_page.setItem(j-1, 1, item)
            checkbox = QTableWidgetItem()
            checkbox.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            checkbox.setTextAlignment(Qt.AlignCenter)
            self.uic.tablewidget_page.setItem(j-1, 0, checkbox)
            i = 2
            for value in data.values():
                if i == 2:
                    id_object = value
                if i == 11:
                    if self.updateDay:
                        value = '0'
                        self.db.updateOneAccount(id_object, {'xuhnay': value})
                if i != 12:
                    item = QTableWidgetItem(str(value))
                    item.setForeground(QColor(84, 110, 122))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.uic.tablewidget_page.setItem(j-1, i, item)
                i += 1
                matches = [element for element in self.listThreadRunning if j-1 == element]
                if matches == []:
                    self.btnOpen = QPushButton('&Mở', clicked=self.__startOneThread)
                    self.uic.tablewidget_page.setCellWidget(j-1, 14, self.btnOpen)
                    self.btnOpen.setStyleSheet("background-color: rgb(33, 150, 243); font-size: 11px; border-radius: 5px; color: white; margin-left: 13px; margin-right: 13px")

                combo = TransparentComboBox()
                combo.addItems(combo_items)
                combo.setCurrentText(str(value))
                self.uic.tablewidget_page.setCellWidget(j-1, 12, combo)
            j+=1
        self.uic.tablewidget_page.setItemDelegate(ColorDelegate())
        self.uic.tablewidget_page.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.uic.tablewidget_page.setColumnHidden(2, True)
        self.uic.taskbar_tatca.setText(f"Tất cả: {self.count}")
        if noti: Information("Tải lại danh sách tài khoản thành công.")
    def setSizeColumn(self):
        self.uic.tablewidget_page.setColumnWidth(0, 50) # check box
        self.uic.tablewidget_page.setColumnWidth(1, 50) # STT
        self.uic.tablewidget_page.setColumnWidth(3, 50) # Session
        self.uic.tablewidget_page.setColumnWidth(4, 50) # Name phone
        self.uic.tablewidget_page.setColumnWidth(5, 150) # Device
        self.uic.tablewidget_page.setColumnWidth(6, 70) # Version adr
        self.uic.tablewidget_page.setColumnWidth(7, 70) # User tiktok
        self.uic.tablewidget_page.setColumnWidth(8, 120) # UserTDS
        self.uic.tablewidget_page.setColumnWidth(9, 100) # PwdTDS
        self.uic.tablewidget_page.setColumnWidth(10, 70) # Xu
        self.uic.tablewidget_page.setColumnWidth(11, 70) # Xu hnay
        self.uic.tablewidget_page.setColumnWidth(12, 50) # Job
        self.uic.tablewidget_page.setColumnWidth(13, 50) # vpn
        self.uic.tablewidget_page.setColumnWidth(14, 80) # Thao tác
        self.uic.tablewidget_page.setColumnWidth(15, 250) # Status
        self.uic.tablewidget_page.setColumnWidth(16, 100) # Lần chạy cuối
    def setColorStatusTable(self, row, column, status='', center=True):
        item = QTableWidgetItem(str(status))
        item.setForeground(QColor(84, 110, 122))
        if center: item.setTextAlignment(Qt.AlignCenter)
        self.uic.tablewidget_page.setItem(row, column, item)
   
    # setting show
    def saveSettingShow(self):
        session = self.uic.box_session.isChecked()
        phonename = self.uic.box_phonename.isChecked()
        version = self.uic.box_version.isChecked()
        device = self.uic.box_device.isChecked()
        unique_tiktok = self.uic.box_uniquetiktok.isChecked()
        username = self.uic.box_username.isChecked()
        password = self.uic.box_password.isChecked()
        total = self.uic.box_total.isChecked()
        hnay = self.uic.box_hnay.isChecked()
        vpn = self.uic.box_vpn.isChecked()
        timelast = self.uic.box_timelast.isChecked()
        cache = self.uic.box_cache.isChecked()
        accrun = self.uic.box_acc_run.isChecked()
        jobday = self.uic.box_jobday.isChecked()
        # secolumn table 
        self.checkShowColumn(session, phonename, version, device, unique_tiktok, username, 
                            password, total, hnay, vpn, timelast, cache, accrun, jobday)
        # save setting show
        new_setting = {
            'session': session,
            'name_phone': phonename,
            'version': version,
            'device': device,
            'unique_tiktok': unique_tiktok,
            'username': username,
            'password': password,
            'total': total,
            'hnay': hnay,
            'vpn': vpn,
            'timelast': timelast,
            'cache': cache,
            'accrun': accrun,
            'jobday': jobday
        }
        self.db.updateSettingShow(new_setting)
        self.loadSettingShow()
        Information("Lưu cấu hình hiển thị thành công")
    def loadSettingShow(self):
        show = self.db.getSettingShow()
        self.uic.box_session.setChecked(show['session'])
        self.uic.box_phonename.setChecked(show['name_phone'])
        self.uic.box_version.setChecked(show['version'])
        self.uic.box_device.setChecked(show['device'])
        self.uic.box_uniquetiktok.setChecked(show['unique_tiktok'])
        self.uic.box_username.setChecked(show['username'])
        self.uic.box_password.setChecked(show['password'])
        self.uic.box_total.setChecked(show['total'])
        self.uic.box_hnay.setChecked(show['hnay'])
        self.uic.box_vpn.setChecked(show['vpn'])
        self.uic.box_timelast.setChecked(show['timelast'])
        self.uic.box_cache.setChecked(show['cache'])
        self.uic.box_acc_run.setChecked(show['accrun'])
        self.uic.box_jobday.setChecked(show['jobday'])

        self.checkShowColumn(show['session'], show['name_phone'], show['version'], show['device'], show['unique_tiktok'], show['username'], show['password'], show['total'], show['hnay'],
                                show['vpn'], show['timelast'], show['cache'], show['accrun'], show['jobday'])
    def checkShowColumn(self, session, phonename, version, device, unique_tiktok, username, 
                                password, total, hnay, vpn, timelast, cache, accrun, jobday):
        self.uic.tablewidget_page.setColumnHidden(3, not session) # session
        self.uic.tablewidget_page.setColumnHidden(4, not phonename) # Phone name
        self.uic.tablewidget_page.setColumnHidden(5, not device) # Device
        self.uic.tablewidget_page.setColumnHidden(6, not version) # Phone name
        self.uic.tablewidget_page.setColumnHidden(7, not unique_tiktok) # Unique tiktok
        self.uic.tablewidget_page.setColumnHidden(8, not username) # Username
        self.uic.tablewidget_page.setColumnHidden(9, not password) # Password
        self.uic.tablewidget_page.setColumnHidden(10, not total) # Total
        self.uic.tablewidget_page.setColumnHidden(11, not hnay) # Hnay
        self.uic.tablewidget_page.setColumnHidden(12, not vpn) # Vpn
        self.uic.tablewidget_page.setColumnHidden(13, not cache) # cache
        # self.uic.tablewidget_page.setColumnHidden(13, not cache) # accrun
        # self.uic.tablewidget_page.setColumnHidden(13, not cache) # jobday
        self.uic.tablewidget_page.setColumnHidden(16, not timelast) # Last time

    # table
    def showMenu(self):
        # TABLE WIDGET
        width = self.uic.leftMenu.width()
        maxExtend = 50
        standard = 150

        # SET MAX WIDTH
        if width == 150:
            widthExtended = maxExtend
        else:
            widthExtended = standard
        # ANIMATION
        self.animation = QPropertyAnimation(self.uic.leftMenu, b"maximumWidth")
        self.animation.setDuration(0)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
    def showFarmExtra(self):
        pass
    def showHistory(self):
        width = self.uic.frame_cauhinh.width()
        maxExtend = 800
        standard = 0
        # SET MAX WIDTH
        if width == 0 or width == 801:
            widthExtended = maxExtend
        else:
            widthExtended = standard
        # ANIMATION
        self.animation = QPropertyAnimation(self.uic.frame_cauhinh, b"minimumWidth")
        self.animation.setDuration(0)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        self.uic.stackedWidget_setting.setCurrentWidget(self.uic.page_tacvu)
        self.function_reset = 3
    def showCauHinhTool(self):
        self.uic.stackedWidget_setting.setCurrentWidget(self.uic.page_cauhinh)
        width = self.uic.frame_cauhinh.width()
        self.maxExtend = 801
        standard = 0

        # SET MAX WIDTH
        if width == 0 or width == 800:
            widthExtended = self.maxExtend
        else:
            widthExtended = standard
        # ANIMATION
        self.animation = QPropertyAnimation(self.uic.frame_cauhinh, b"minimumWidth")
        self.animation.setDuration(0)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        self.function_show = 2
        self.function_reset = 2
    def showAddAccount(self):
        self.arr_account_add = []
        self.uic.plain_add.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.uic.stackedWidget_setting.setCurrentWidget(self.uic.page_add)
        width = self.uic.frame_cauhinh.width()
        maxExtend = 800
        standard = 0

        # SET MAX WIDTH
        if width == 0 or width == 801:
            widthExtended = maxExtend
        else:
            widthExtended = standard
        # ANIMATION
        self.animation = QPropertyAnimation(self.uic.frame_cauhinh, b"minimumWidth")
        self.animation.setDuration(0)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        self.function_show = 1
        self.function_reset = 1
        self.uic.plain_add.textChanged.connect(self.custom_keyPressEvent)
    def showColumnTable(self):
        self.arr_account_add = []
        self.uic.btn_savecmd.setVisible(True)
        self.uic.btn_reset.setVisible(True)
        self.uic.btn_savecmd.setText("Lưu cài đặt")
        self.uic.plain_add.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.uic.stackedWidget_setting.setCurrentWidget(self.uic.page_show)
        width = self.uic.frame_cauhinh.width()
        maxExtend = 800
        standard = 0

        # SET MAX WIDTH
        if width == 0 or width == 801:
            widthExtended = maxExtend
        else:
            widthExtended = standard
        # ANIMATION
        self.animation = QPropertyAnimation(self.uic.frame_cauhinh, b"minimumWidth")
        self.animation.setDuration(0)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        self.function_show = 4
        self.function_reset = 4
        self.uic.plain_add.textChanged.connect(self.custom_keyPressEvent)
    def custom_keyPressEvent(self):
        text = self.uic.plain_add.toPlainText().strip()
        values = text.split("\n")
        self.arr_account_add = [x for x in values if x.strip()]
        num_values = len(self.arr_account_add)
        self.uic.add_tong.setText(f"Tổng: {num_values}")
    def clickedSaveSetting(self):
        if self.function_show == 1:
            self.addAccountDB()
        elif self.function_show == 2:
            self.saveSetting()
        elif self.function_show == 4:
            self.saveSettingShow()
    
    # TABLE ROW GET EVENT
    def GetXY(self, selec):
        for i in selec.indexes():
            self.row = i.row()
        self.userSelectedCheckboxList = list(set(self.getRow()))
        self.uic.taskbar_boiden.setText(f"Bôi đen: {len(self.userSelectedCheckboxList)}")
        try:
            self.uid = self.uic.tablewidget_page.item(self.row,0).text()
        except: pass
    def getRow(self):
        list_row = []
        for current in self.uic.tablewidget_page.selectedItems():
            row = current.row()
            list_row.append(row)
        return list_row
    def onCellChange(self, row):
        try: checkBox = self.uic.tablewidget_page.item(row, 0).checkState()
        except: return
        # if checkBox == 2: 
        #     self.count_checked += 1
        # else:
        #     if self.count_checked > 0:
        #         self.count_checked -= 1
        # print(checkBox, self.count_checked)
        # self.uic.taskbar_dachon.setText(f"Đã chọn: {self.count_checked}")

    # main tool, private
    def __startOneThread(self):
        matches = [element for element in self.listThreadRunning if self.row == element]
        if matches:
            Information("Luồng đang hoạt động, không thể khởi tạo")
        else:
            self.btnOpen = QPushButton('&Đóng', clicked=self.__stopOneThread)
            self.uic.tablewidget_page.setCellWidget(self.row, 14, self.btnOpen)
            self.btnOpen.setStyleSheet("background-color: rgb(255, 85, 0); font-size: 11px; border-radius: 5px; color: white; margin-left: 13px; margin-right: 13px")
            object_id = self.uic.tablewidget_page.item(self.row, 2).text()
            session = self.uic.tablewidget_page.item(self.row, 3).text()
            phone_name = self.uic.tablewidget_page.item(self.row, 4).text()
            phone_device = self.uic.tablewidget_page.item(self.row, 5).text()
            ver_adr = self.uic.tablewidget_page.item(self.row, 6).text()
            user_tiktok = self.uic.tablewidget_page.item(self.row, 7).text()
            usertds = self.uic.tablewidget_page.item(self.row, 8).text()
            pwdtds = self.uic.tablewidget_page.item(self.row, 9).text()
            xu_tds = self.uic.tablewidget_page.item(self.row, 10).text()
            xu_hnay = self.uic.tablewidget_page.item(self.row, 11).text()
            vpn = self.uic.tablewidget_page.cellWidget(self.row, 12).currentText()

            self.db.updateOneAccount(object_id, {'vpn': vpn})
            self.threadStartChrome[self.row] = threadToolTds({
                'row': self.row,
                'object_id': object_id, 
                'session': session,
                'phone_name': phone_name,
                'phone_device': phone_device,
                'version': ver_adr,
                'user_tiktok': user_tiktok,
                'usertds': usertds,
                'pwdtds': pwdtds,
                'xu': xu_tds,
                'xu_hnay': xu_hnay,
                'vpn': vpn,
                'getMail': self.getMail,
                'apiKeyTaphoa': self.apiKeyTaphoa,
                'keyShop': self.keyShop,
                'apikey1st': self.apikey1st,
                'dlMin': self.dlMin,
                'dlMax': self.dlMax,
                'path_image': self.path_image,
                'limitXu': self.limitXu,
                'stopSleep': self.stopSleep,
                'limitStopAcc': self.limitStopAcc
            })
            self.threadStartChrome[self.row].start()
            self.threadStartChrome[self.row].sendDataUpMainScreen.connect(self.__showHistoryData)
            self.listThreadRunning.append(self.row)
        if self.listThreadRunning == []:
            self.uic.btn_dunglai.setEnabled(False)
        else:
            self.uic.btn_dunglai.setEnabled(True)
    def __stopOneThread(self):
        self.btnOpen = QPushButton('&Mở', clicked=self.__startOneThread)
        self.uic.tablewidget_page.setCellWidget(self.row, 14, self.btnOpen)
        self.btnOpen.setStyleSheet("background-color: rgb(33, 150, 243); font-size: 11px; border-radius: 5px; color: white; margin-left: 13px; margin-right: 13px")
        Thread(target=self.__threadStop, args=(self.row, )).start()
    def __startMultiThread(self):
        self.uic.btn_dunglai.setEnabled(True)
        for row in range(self.uic.tablewidget_page.rowCount()):
            isCheck = self.uic.tablewidget_page.item(row, 0).checkState()
            if isCheck == 2: # 2 check được chọn 0 là chưa được chọn
                matches = [element for element in self.listThreadRunning if row == element]
                if matches:
                    return Information("Luồng đang hoạt động, không thể khởi tạo")
                else:
                    object_id = self.uic.tablewidget_page.item(row, 2).text()
                    session = self.uic.tablewidget_page.item(row, 3).text()
                    phone_name = self.uic.tablewidget_page.item(row, 4).text()
                    phone_device = self.uic.tablewidget_page.item(row, 5).text()
                    ver_adr = self.uic.tablewidget_page.item(row, 6).text()
                    user_tiktok = self.uic.tablewidget_page.item(row, 7).text()
                    usertds = self.uic.tablewidget_page.item(row, 8).text()
                    pwdtds = self.uic.tablewidget_page.item(row, 9).text()
                    xu_tds = self.uic.tablewidget_page.item(row, 10).text()
                    xu_hnay = self.uic.tablewidget_page.item(row, 11).text()
                    vpn = self.uic.tablewidget_page.cellWidget(row, 12).currentText()
                    
                    self.db.updateOneAccount(object_id, {'vpn': vpn})
                    self.btnOpen = QPushButton('&Đóng', clicked=self.__stopOneThread)
                    self.uic.tablewidget_page.setCellWidget(row, 14, self.btnOpen)
                    self.btnOpen.setStyleSheet("background-color: rgb(255, 85, 0); font-size: 11px; border-radius: 5px; color: white; margin-left: 13px; margin-right: 13px")
                    self.threadStartChrome[row] = threadToolTds({
                        'row': row,
                        'object_id': object_id, 
                        'session': session,
                        'phone_name': phone_name,
                        'phone_device': phone_device,
                        'version': ver_adr,
                        'user_tiktok': user_tiktok,
                        'usertds': usertds,
                        'pwdtds': pwdtds,
                        'xu': xu_tds,
                        'xu_hnay': xu_hnay,
                        'vpn': vpn,
                        'getMail': self.getMail,
                        'apiKeyTaphoa': self.apiKeyTaphoa,
                        'keyShop': self.keyShop,
                        'apikey1st': self.apikey1st,
                        'dlMin': self.dlMin,
                        'dlMax': self.dlMax,
                        'path_image': self.path_image,
                        'limitXu': self.limitXu,
                        'stopSleep': self.stopSleep,
                        'limitStopAcc': self.limitStopAcc
                    })
                    self.threadStartChrome[row].start()
                    self.threadStartChrome[row].sendDataUpMainScreen.connect(self.__showHistoryData)
                    self.listThreadRunning.append(row)
        print(self.listThreadRunning)
    def __stopMultiThread(self):
        for row in range(self.uic.tablewidget_page.rowCount()):
            isCheck = self.uic.tablewidget_page.item(row, 0).checkState()
            if isCheck == 2: # 2 check được chọn 0 là chưa được chọn
                self.btnOpen = QPushButton('&Mở', clicked=self.__startOneThread)
                self.uic.tablewidget_page.setCellWidget(row, 14, self.btnOpen)
                self.btnOpen.setStyleSheet("background-color: rgb(33, 150, 243); font-size: 11px; border-radius: 5px; color: white; margin-left: 13px; margin-right: 13px")
                Thread(target=self.__threadStop, args=(row, )).start()
        if len(self.listThreadRunning) == 0:
            self.uic.btn_dunglai.setEnabled(False)
            self.uic.btn_batdau.setEnabled(True)
        print(self.listThreadRunning)
    def __threadStop(self, row):
        try:
            self.listThreadRunning.remove(row)
            self.threadStartChrome[row].stop()
            self.threadStartChrome[row].wait()
            self.threadStartChrome[row].quit()
        except: pass
    def __checkXuAll(self):
        xu = 0
        xhnay = 0
        for row in range(self.uic.tablewidget_page.rowCount()):
            xu_tds = self.uic.tablewidget_page.item(row, 10).text().replace(',','')
            xu_hnay = self.uic.tablewidget_page.item(row, 11).text().replace(',','')
            xu += int(xu_tds)
            xhnay += int(xu_hnay)
        Information(f"Tổng xu: {'{:,}'.format(xu)}\nXu hôm nay: {'{:,}'.format(xhnay)}")
    def __sendXu(self):
        usertds = self.uic.tablewidget_page.item(self.row, 8).text()
        pwdtds = self.uic.tablewidget_page.item(self.row, 9).text()
        dlg = senXuDialog(usertds, pwdtds)
        dlg.exec_()
    def __changePwdTds(self):
        list_object = []
        list_row = []
        x = 0
        for row in range(self.uic.tablewidget_page.rowCount()):
            isCheck = self.uic.tablewidget_page.item(row, 0).checkState()
            if isCheck == 2: # 2 check được chọn 0 là chưa được chọn
                object_id = self.uic.tablewidget_page.item(row, 2).text()
                list_object.append(object_id)
                list_row.append(row)
                x += 1
        if x == 0:
            return Information("Vui lòng chọn tài khoản cần thay đổi mật khẩu.")
        dlg = changPwdDialog(self.uic, list_row, list_object)
        dlg.exec_()

    # show history tool
    def __showHistoryData(self, dict_data):
        code         = dict_data['code']
        row          = dict_data['row']
        object_id    = dict_data['object_id']
        session      = dict_data['session']
        phone_name   = dict_data['phone_name']
        ver_adr      = dict_data['ver_adr']
        user_tiktok  = dict_data['user_tiktok']
        usertds      = dict_data['usertds']
        pwdtds       = dict_data['pwdtds']
        xu           = dict_data['xu']
        xuhnay       = dict_data['xuhnay']
        cache        = dict_data['cache']
        status       = dict_data['status']
        cur_time = getCurrentTime()['time']
        if code == 100:
            self.setColorStatusTable(row, 13, cache)
            self.setColorStatusTable(row, 15, status, center=False)
        elif code == 200:
            self.setColorStatusTable(row, 3, session)
            self.setColorStatusTable(row, 6, ver_adr)
            self.setColorStatusTable(row, 7, user_tiktok)
            self.setColorStatusTable(row, 8, usertds)
            self.setColorStatusTable(row, 9, pwdtds)
            self.setColorStatusTable(row, 10, xu)
            self.setColorStatusTable(row, 11, xuhnay)
            self.setColorStatusTable(row, 15, status, center=False)
            self.setColorStatusTable(row, 16, cur_time)
            item = QListWidgetItem(f"[ {cur_time} ] : [ Thread: {row} ] : [ {status} ]")
            self.uic.listWidget_history.addItem(item)
            new_dict_data = {
                'session': session,
                'phone': phone_name,
                'version': ver_adr,
                'user_tiktok': user_tiktok,
                'usertds': usertds,
                'pwdtds': pwdtds,
                'xu': xu,
                'xuhnay': xuhnay
            }
            self.db.updateOneAccount(object_id, new_dict_data)
        elif code == 204:
            self.setColorStatusTable(row, 15, status, center=False)
            item = QListWidgetItem(f"[ {cur_time} ] : [ Thread: {row} ] : [ {status} ]")
            self.uic.listWidget_history.addItem(item)
            self.btnOpen = QPushButton('&Mở', clicked=self.__startOneThread)
            self.uic.tablewidget_page.setCellWidget(row, 14, self.btnOpen)
            self.btnOpen.setStyleSheet("background-color: rgb(33, 150, 243); font-size: 11px; border-radius: 5px; color: white; margin-left: 13px; margin-right: 13px")
            try: self.listThreadRunning.remove(row)
            except: pass

class threadToolTds(QThread):
    sendDataUpMainScreen = pyqtSignal(object)
    def __init__(self, dataWindow):
        super(threadToolTds, self).__init__()
        self.mutex = QMutex()
        self.event = Event()
        self.row            = dataWindow['row']
        self.folder         = self.row+1
        object_id           = dataWindow['object_id']
        self.session        = dataWindow['session']
        phone_name          = dataWindow['phone_name']
        self.phone_device   = dataWindow['phone_device']
        self.ver_adr        = dataWindow['version']
        self.user_tiktok    = dataWindow['user_tiktok']
        self.usertds        = dataWindow['usertds']
        self.pwdtds         = dataWindow['pwdtds']
        self.xu             = dataWindow['xu']
        self.xuhnay         = dataWindow['xu_hnay']
        self.vpn            = dataWindow['vpn']
        self.getMail        = dataWindow['getMail']
        self.apiKeyTaphoa   = dataWindow['apiKeyTaphoa']
        self.keyShop        = dataWindow['keyShop']
        self.apikey1st      = dataWindow['apikey1st']
        self.dlMin          = dataWindow['dlMin']
        self.dlMax          = dataWindow['dlMax']
        self.folder_image   = dataWindow['path_image']
        # self.timeStart      = dataWindow['timeStart']      
        # self.timeEnd        = dataWindow['timeEnd']
        self.limitXu        = dataWindow['limitXu']
        self.stopSleep      = dataWindow['stopSleep']
        self.limitStopAcc   = dataWindow['limitStopAcc']


        self.dict_data = {
            'code': 100,
            'row': self.row,
            'object_id': object_id,
            'session': self.session,
            'phone_name': phone_name,
            'ver_adr': self.ver_adr,
            'user_tiktok': self.user_tiktok,
            'usertds': self.usertds,
            'pwdtds': self.pwdtds,
            'xu': self.xu,
            'xuhnay': self.xuhnay,
            'cache': '0',
            'status': ''
        }
        api_code = """
            100 -> Phản hồi thông tin - Yêu cầu đã được chấp nhận và đang xử lý - pending
            200 -> Phản hồi thành công - Yêu cầu được chấp nhận - OK
            204 -> Phản hồi thất bại - Yêu cầu đã được máy chủ tiếp nhận - failed
        """
        self.adb = ADB_TOOL(self.phone_device)
        del dataWindow
    
    def run(self):
        self.dict_data.update({'code': 100, 'status': 'Đang bắt đầu chạy.'})
        self.sendDataUpMainScreen.emit(self.dict_data)

        # check path image
        path = self.randomPictures(self.folder_image)
        if path == 'NO_PATH_IMAGE':
            self.dict_data.update({'code': 204, 'status': 'Đường dẫn hình ảnh không tồn tại'})
            return self.sendDataUpMainScreen.emit(self.dict_data)

        # Check tds
        getAccount = API_TDS().getTokenTds(self.usertds, self.pwdtds)
        print(self.row, getAccount)
        if getAccount == {}:
            self.dict_data.update({'code': 204, 'status': 'Sai tài khoản / mật khẩu'})
            return self.sendDataUpMainScreen.emit(self.dict_data)
        self.access_token = getAccount['access_token']
        xu = getAccount['xu']
        self.tds = API_TDS(self.access_token)

        android9 = False
        android8 = False
        android7 = False
        nhanxuloi = 0
        upload = False
        gmail = ''
        total_xu_them = int(self.xuhnay.replace(',', ''))
        

        # check version android
        version_android = self.adb.checkVerisonAndroid()
        if not version_android:
            self.dict_data.update({'code': 204, 'status': 'Không thể kết nối tới máy chủ'})
            return self.sendDataUpMainScreen.emit(self.dict_data)
        self.dict_data.update({'code': 200, 'ver_adr': version_android, 'xu': xu, 'status': f'Lấy thành công thông tin tài khoản và thiết bị.'})
        self.sendDataUpMainScreen.emit(self.dict_data)
        if version_android.strip() == "9":
            android9 = True
        elif version_android.split('.')[0] == "8":
            android8 = True
        elif version_android.split('.')[0] == "7":
            android7 = True

        while True:
            try:
                if self.getMail == 'file':
                    with open(f'data\\mail\\stream\\{self.folder}\\gmail.txt', 'r', encoding='utf-8') as file:
                        self.arr_gmail = file.readlines()
                    with open(f'data\\mail\\stream\\{self.folder}\\gmail_done.txt', 'r', encoding='utf-8') as file:
                        self.arr_gmail_done = file.readlines()
                    arr_gmaildone = self.duplicateFilter() # lọc trùng gmail done
                    if len(self.arr_gmail) == len(arr_gmaildone):
                        # with open(f'data\\mail\\stream\\{self.folder}\\gmail_done.txt', 'w', encoding='utf-8') as file: pass
                        self.dict_data.update({'code': 204, 'status': f'Tất cả gmail trong file đã được sử dụng.'})
                        return self.sendDataUpMainScreen.emit(self.dict_data)
                # start thread tool
                xumotacc = 0
                ngaysinh = False
                if self.session == 'FAIL':
                    # xóa data tiktok
                    self.dict_data.update({'code': 100, 'status': 'Đóng tiktok và xóa dữ liệu app'})
                    self.sendDataUpMainScreen.emit(self.dict_data)
                    self.clearDataTiktok()

                    if nhanxuloi >= 2:
                        for t in range(3600, -1, -1):
                            self.dict_data.update({'code': 100, 'status': f'Máy bị nhả, nghỉ {t} giây ...'})
                            self.sendDataUpMainScreen.emit(self.dict_data)
                            sleep(1)
                    # Tắt VPN
                    self.dict_data.update({'code': 100, 'status': f'Tiến hành tắt VPN {self.vpn}'})
                    self.sendDataUpMainScreen.emit(self.dict_data)
                    self.changeVPN(change=False, off=True)

                    for _ in range(4):
                        # Xóa tài khoản google
                        self.dict_data.update({'code': 100, 'status': f'Tiến hành xóa tài khoản google'})
                        self.sendDataUpMainScreen.emit(self.dict_data)

                        self.adb.runShell("am start -a android.settings.SYNC_SETTINGS") # mở mục tài khoản
                        self.adb.runShell("settings put system accelerometer_rotation 0") # khóa màn hình dọc
                        self.adb.runShell("input swipe 588 300 577 1600 100") # vuốt lên đầu
                        
                        # Android 9
                        if android9:
                            for _ in range(10):
                                if self.adb.find_image('img\\ggacc.png', 5, row=self.row):
                                    self.adb.find_image('img\\xoatk9.png', 5, threshold=0.8, row=self.row)
                                    self.adb.find_image('img\\xoatk9xn.png', 5, threshold=0.8, row=self.row)
                                    sleep(3)
                                else: break
                        # Android 8
                        if android8:
                            for _ in range(10):
                                if self.adb.find_image('img\\ggacc.png', 2, row=self.row):
                                    # sleep(2)
                                    if self.adb.find_image('img\\ggacc.png', 2, click=False, row=self.row):
                                        # sleep(1)
                                        self.adb.find_image('img\\xoataikhoan8.png', 3, row=self.row)
                                        # sleep(1)
                                        self.adb.find_image('img\\xoataikhoan8xn.png', 3, row=self.row)
                                    sleep(3)
                                else: break
                        # Android 7
                        if android7:
                            if self.adb.find_image('img\\ggacc.png', 2, row=self.row):
                                for _ in range(10):
                                    if self.adb.find_image('img\\taikhoan7.png', 2, click=False, row=self.row):
                                        cord = self.adb.find_image('img\\taikhoan7.png', 2, screenshot=False, cord=True, row=self.row)
                                        if cord != False:
                                            x = cord['x2']
                                            y = cord['y2']
                                            self.adb.clicks(x, y+140, 1)
                                            # sleep(1)
                                            self.adb.find_image('img\\3cham.png', 3, row=self.row)
                                            # sleep(1)
                                            self.adb.find_image('img\\xoatk7.png', 3, row=self.row)
                                            # sleep(1)
                                            self.adb.find_image('img\\xoataikhoan7.png', 3, row=self.row)
                                    elif self.adb.find_image('img\\ggacc.png', 2, click=False, row=self.row):
                                        self.adb.find_image('img\\3cham.png', 3, row=self.row)
                                        self.adb.find_image('img\\xoatk7.png', 3, row=self.row)
                                        if self.adb.find_image('img\\xoataikhoan7.png', 3, row=self.row):
                                            break
                                    else:
                                        break
                        
                        self.adb.runShell("am force-stop com.android.settings")
                        self.dict_data.update({'code': 100, 'status': 'Xóa tài khoản google thành công'})
                        self.sendDataUpMainScreen.emit(self.dict_data)

                        if self.getMail == 'api': # file
                            self.dict_data.update({'code': 100, 'status': 'Đang tranh giành gmail'})
                            self.sendDataUpMainScreen.emit(self.dict_data)
                            gmail = self.muaMail()
                            gmail_t = gmail.split('|')
                        elif self.getMail == 'file': 
                            # self.mutex.lock()
                            for m in range(len(self.arr_gmail)):
                                gmail = self.arr_gmail[m].strip()
                                if gmail not in str(self.arr_gmail_done):
                                    gmail_t = gmail.split('|')
                                    break
                            # self.mutex.unlock()
                        if gmail == '':
                            self.dict_data.update({'code': 204, 'status': f'Tất cả gmail trong file đã được sử dụng.'})
                            return self.sendDataUpMainScreen.emit(self.dict_data)

                        self.pwd_gmail = gmail_t[1].strip()

                        # Đăng nhập google
                        ggCheck = True
                        login = False
                        for _ in range(5):    
                            self.dict_data.update({'code': 100, 'status': f'Đăng nhập google lần {_} '})
                            self.sendDataUpMainScreen.emit(self.dict_data)
                            for _ in range(5):
                                self.adb.runShell('am start -a android.settings.ADD_ACCOUNT_SETTINGS')
                                self.adb.runShell("settings put system accelerometer_rotation 0")
                                if self.adb.find_image('img\\gg_8.png', 3, row=self.row):
                                    ggCheck = True
                                    break
                                else:
                                    ggCheck = False
                                    self.adb.runShell("input keyevent 4")
                                    self.adb.runShell("input keyevent 4")
                                    self.adb.runShell("input keyevent 4")
                                    self.adb.runShell("input keyevent 4")
                            if ggCheck == False:
                                continue
                            self.dict_data.update({'code': 100, 'status': f'Nhập tài khoản mật khẩu'})
                            self.sendDataUpMainScreen.emit(self.dict_data)
                            self.adb.find_image('img\\logogg.png', 10, click=False, row=self.row)
                            self.adb.clicks(270, 730, 1)
                            sleep(2)
                            self.adb.send_keys(gmail_t[0])
                            self.adb.runShell("input keyevent 66") # enter
                            sleep(5)
                            self.adb.find_image('img\\logogg.png', 5, click=False, row=self.row)
                            sleep(2)
                            self.adb.send_keys(gmail_t[1].strip())
                            self.adb.runShell("input keyevent 66") # enter
                            sleep(2)
                            self.dict_data.update({'code': 100, 'status': f'Chấp nhận điều khoản google'})
                            self.sendDataUpMainScreen.emit(self.dict_data)
                            
                            login = False
                            if android9:
                                for _ in range(10):
                                    self.adb.runShell("input swipe 1000 959 1000 400 50")
                                    if self.adb.find_image('img\\toihieu9.png', 1, row=self.row) == False:
                                        self.adb.find_image('img\\toihieu_en.png', 1, row=self.row)
                                    sleep(3)
                                    if self.adb.find_image('img\\toidongy9.png', 1, row=self.row) == False:
                                        self.adb.find_image('img\\toidongy_en.png', 1, row=self.row)
                                    if self.adb.find_image('img\\chapnhan9.png', 1, row=self.row):
                                        login = True
                                        break

                            if android8 or android7:
                                for _ in range(10):
                                    self.adb.runShell("input swipe 224 1435 143 285 100")
                                    self.adb.find_image('img\\chapnhan_en_8.png', 1, row=self.row)
                                    self.adb.find_image('img\\dongy_en_8.png', 1, screenshot=False, row=self.row)
                                    self.adb.find_image('img\\toihieu_8.png', 1, screenshot=False, row=self.row)
                                    self.adb.find_image('img\\toidongy_8.png', 1, screenshot=False, row=self.row)
                                    if self.adb.find_image('img\\chapnhan_done_8.png', 1, screenshot=False, row=self.row) or self.adb.find_image('img\\accept8.png', 1, screenshot=False, row=self.row) or self.adb.find_image('img\\added.png', 1, screenshot=False, row=self.row):
                                        login = True
                                        break
                            
                            if login == False:
                                # check đăng nhập
                                self.dict_data.update({'code': 100, 'status': f'Kiểm tra lại đăng nhập google'})
                                self.sendDataUpMainScreen.emit(self.dict_data)
                                self.adb.runShell("am start -a android.settings.SYNC_SETTINGS")
                                self.adb.runShell("settings put system accelerometer_rotation 0")
                                self.adb.runShell("input swipe 588 300 577 1600 100") # vuốt lên đầu
                                if self.adb.find_image('img\\ggacc.png', 10, click=False, row=self.row):
                                    self.dict_data.update({'code': 100, 'status': f'Đăng nhập google thành công'})
                                    self.sendDataUpMainScreen.emit(self.dict_data)
                                    login = True
                                    break
                                else:
                                    self.dict_data.update({'code': 100, 'status': f'Đăng nhập google thất bại'})
                                    self.sendDataUpMainScreen.emit(self.dict_data)
                                    login = False
                            else: 
                                self.dict_data.update({'code': 100, 'status': f'Đăng nhập google thành công'})
                                self.sendDataUpMainScreen.emit(self.dict_data)
                                break
                        if login == False: continue
                        else: break

                    self.adb.runShell("am force-stop com.android.settings") 

                    # Bật VPN
                    self.dict_data.update({'code': 100, 'status': f'Tiến hành bật VPN {self.vpn}'})
                    self.sendDataUpMainScreen.emit(self.dict_data)
                    self.changeVPN(change=True, off=False)

                    # Mở tiktok
                    self.dict_data.update({'code': 100, 'status': f'Tiến hành mở tiktok'})
                    self.sendDataUpMainScreen.emit(self.dict_data)
                    self.adb.runShell("monkey -p com.ss.android.ugc.trill -c android.intent.category.LAUNCHER 1")
                    self.adb.runShell("settings put system accelerometer_rotation 0")
                    sleep(10)
                    # if self.adb.find_image('img\\boqua.png', 10, click=False, row=self.row) == False:
                    if self.adb.checkXml(CountRepeat=5, element='//node[@text="Bỏ qua"]', click=False) == False:
                        self.adb.clicks(550, 1210, 1)
                        sleep(2)
                        self.adb.clicks(530, 1111, 1)
                    self.adb.checkXml(CountRepeat=5, element='//node[@text="Bỏ qua"]')
                    sleep(5)
                    self.adb.runShell("input swipe 224 1435 143 285 100")

                    # vô trang chủ
                    ngaysinh = True
                    for _ in range(8):
                        self.adb.runShell("monkey -p com.ss.android.ugc.trill -c android.intent.category.LAUNCHER 1")
                        self.adb.runShell("settings put system accelerometer_rotation 0")
                        sleep(7)
                        self.dict_data.update({'code': 100, 'status': 'Tắt các quảng cáo ở trang chủ, tiến hành đăng ký'})
                        self.sendDataUpMainScreen.emit(self.dict_data)
                        if self.adb.find_image('img\\user_8.png', 1, click=False, threshold=0.8, row=self.row) == False and (self.adb.find_image('img\\tuchoi_8.png', 1, row=self.row) == False or self.adb.find_image('img\\tuchoi9.png', 1, row=self.row) == False):
                            self.adb.clicks(550, 1210, 1) # click điều khoản 
                            sleep(2)
                            self.adb.clicks(530, 1111, 1) # click ok
                        for _ in range(2):
                            # đóng các quảng cáo của tiktok
                            self.adb.runShell("input keyevent 4")
                            sleep(3)
                            self.adb.runShell("input keyevent 4")
                            self.adb.find_image('img\\closequa8.png', 1, threshold=0.6, row=self.row)
                            self.adb.find_image('img\\tuchoi_8.png', 1, row=self.row)
                            self.adb.find_image('img\\tuchoi9.png', 1, row=self.row)
                            self.adb.find_image('img\\closevitri8.png', 1, threshold=0.7, row=self.row)
                            self.adb.find_image('img\\khongchophep.png', 1, row=self.row)
                            self.adb.runShell("input swipe 224 1435 143 285 100")

                        self.dict_data.update({'code': 100, 'status': 'Đang lướt tiktok'})
                        self.sendDataUpMainScreen.emit(self.dict_data)
                        self.adb.runShell("input swipe 224 1435 143 285 100")
                        self.adb.runShell("input swipe 224 1435 143 285 100")
                        self.adb.runShell("input swipe 224 1435 143 285 100")
                        sleep(2)
                        self.dict_data.update({'code': 100, 'status': 'Vô hồ sơ đăng ký.'})
                        self.sendDataUpMainScreen.emit(self.dict_data)
                        self.adb.clicks(969, 1848) # Hồ Sơ
                        sleep(2)
                        if self.adb.find_image('img\\logingmail.png', 5, click=False, row=self.row) or self.adb.find_image('img\\dangky8.png', 5, row=self.row): # check popup
                            # vô hồ sơ đăng ký
                            reg = self.registerTiktok()
                            if reg == 'block_reg':
                                self.dict_data.update({'code': 204, 'status': 'Máy bị chặn reg tài khoản.'})
                                return self.sendDataUpMainScreen.emit(self.dict_data)
                            elif reg == 'registered':
                                self.session = 'OK'
                                if self.getMail == 'file':
                                    with open(f'data\\mail\\stream\\{self.folder}\\gmail_done.txt', "a+", encoding="utf-8") as file:
                                        file.write(gmail + "\n")
                                self.dict_data.update({'code': 200, 'session': self.session, 'status': 'Đăng nhập tiktok thành công'})
                                self.sendDataUpMainScreen.emit(self.dict_data)
                            elif reg == True:
                                self.session = 'OK'
                                if self.getMail == 'file':
                                    with open(f'data\\mail\\stream\\{self.folder}\\gmail_done.txt', "a+", encoding="utf-8") as file:
                                        file.write(gmail + "\n")
                                self.dict_data.update({'code': 200, 'session': self.session, 'status': f'Đăng ký tài khoản tiktok thành công'})
                                self.sendDataUpMainScreen.emit(self.dict_data)
                                if self.adb.checkXml(CountRepeat=5, element='//node[@text="Tài khoản của bạn đã bị cấm vĩnh viễn do vi phạm Hướng dẫn Cộng đồng của chúng tôi nhiều lần."]'):
                                    self.dict_data.update({'code': 204, 'session': 'FAIL', 'status': 'Máy reg tài khoản bị vô hiệu hóa.'})
                                    return self.sendDataUpMainScreen.emit(self.dict_data)
                            else:
                                self.adb.runShell("input keyevent 4")
                                sleep(3)
                                self.adb.runShell("input keyevent 4")
                                sleep(3)
                                self.adb.runShell("input keyevent 4")
                            upload = True
                            break
                    else:
                        # nếu hết 8 lần mà không tìm đc logo tiktok thì quay lại login gmail khác
                        ngaysinh = False
                        self.session = 'FAIL'
                        self.dict_data.update({'code': 200, 'session': self.session, 'status': f'Đăng ký tiktok thất bại'})
                        self.sendDataUpMainScreen.emit(self.dict_data)
                        continue

                self.adb.find_image('img\\tuchoi_8.png', 1, row=self.row)
                self.adb.find_image('img\\tuchoi9.png', 1, row=self.row)
                # end session False
                self.dict_data.update({'code': 100, 'status': 'Đang khởi chạy dữ liệu tiktok'})
                self.sendDataUpMainScreen.emit(self.dict_data)
                check = False
                if self.session == 'OK':
                    for _ in range(10):
                        self.adb.runShell("monkey -p com.ss.android.ugc.trill -c android.intent.category.LAUNCHER 1")
                        sleep(7)
                        self.dict_data.update({'code': 100, 'status': 'Tắt các quảng cáo ở trang chủ, get username'})
                        self.sendDataUpMainScreen.emit(self.dict_data)
                        # tắt các hiển thị quảng cáo
                        for _ in range(2):
                            self.adb.runShell("input keyevent 4")
                            sleep(3)
                            self.adb.runShell("input keyevent 4")
                            self.adb.find_image('img\\closequa8.png', 1, threshold=0.6, row=self.row)
                            self.adb.find_image('img\\tuchoi_8.png', 1, row=self.row)
                            self.adb.find_image('img\\tuchoi9.png', 1, row=self.row)
                            self.adb.find_image('img\\closevitri8.png', 1, threshold=0.7, row=self.row)
                            self.adb.find_image('img\\khongchophep.png', 1, row=self.row)
                            
                        self.adb.find_image('img\\tuchoi_8.png', 1, row=self.row)
                        self.adb.find_image('img\\tuchoi9.png', 1, row=self.row)
                        self.adb.runShell("input swipe 224 1435 143 285 100") # lướt
                        self.adb.runShell("input swipe 224 1435 143 285 100") # lướt
                        self.adb.runShell("input swipe 224 1435 143 285 100") # lướt
                        sleep(2)
                        # check lúc tài khoản được lưu sẵn thì back lại tắt qc, còn reg xong thì k cần back
                        if ngaysinh == False:
                            self.adb.runShell("input keyevent 4")
                            sleep(3)
                            self.adb.runShell("input keyevent 4")
                            sleep(3)
                            self.adb.runShell("input keyevent 4")

                        self.dict_data.update({'code': 100, 'status': 'Tiến hành vào hồ sơ cá nhân'})
                        self.sendDataUpMainScreen.emit(self.dict_data)
                        self.adb.clicks(969, 1848, 1) # Hồ Sơ
                        sleep(2)
                        self.adb.find_image('img\\khongchophep.png', 1, row=self.row)
                        self.adb.runShell("input swipe 588 300 577 1600 100") # vuốt lên đầu
                        if self.adb.find_image('img\\tim.png', 1, click=False, row=self.row) or self.adb.find_image('img\\hs.png', 1, threshold=0.7, click=False, row=self.row):
                            for i in range(3):
                                if self.adb.find_image('img\\tkriengtu8.png', 2, threshold=0.6, click=False, row=self.row):
                                    self.dict_data.update({'code': 100, 'status': 'Chỉnh sửa quyền riêng tư cá nhân'})
                                    self.sendDataUpMainScreen.emit(self.dict_data)
                                    self.adb.find_image('img\\3gach.png', 5, row=self.row)
                                    self.adb.find_image('img\\setting8.png', 5, row=self.row)
                                    self.adb.find_image('img\\riengtu8.png', 5, row=self.row)
                                    self.adb.find_image('img\\onriengtu8.png', 5, row=self.row)
                                    self.adb.find_image('img\\switchriengtu8.png', 5, row=self.row)
                                    self.adb.runShell("input keyevent 4")
                                    self.adb.runShell("input keyevent 4")
                                elif self.adb.find_image('img\\dangky8.png', 5, row=self.row):
                                    try_reg = self.registerTiktok()
                                    if try_reg == 'block_reg':
                                        self.dict_data.update({'code': 204, 'status': 'Máy lỏ bị chặn reg tài khoản.'})
                                        return self.sendDataUpMainScreen.emit(self.dict_data)
                                    elif try_reg == 'registered':
                                        if self.getMail == 'file':
                                            with open(f'data\\mail\\stream\\{self.folder}\\gmail_done.txt', "a+", encoding="utf-8") as file:
                                                file.write(gmail + "\n")
                                        self.dict_data.update({'code': 200, 'session': self.session, 'status': 'Đăng nhập tiktok thành công'})
                                        self.sendDataUpMainScreen.emit(self.dict_data)
                                    elif try_reg == True:
                                        upload = True
                                        if self.getMail == 'file':
                                            with open(f'data\\mail\\stream\\{self.folder}\\gmail_done.txt', "a+", encoding="utf-8") as file:
                                                file.write(gmail + "\n")
                                        self.dict_data.update({'code': 200, 'session': self.session, 'status': f'Đăng ký tài khoản tiktok thành công'})
                                        self.sendDataUpMainScreen.emit(self.dict_data)
                                    else:
                                        self.adb.runShell("input keyevent 4")
                                        sleep(3)
                                        self.adb.runShell("input keyevent 4")
                                        sleep(3)
                                        self.adb.runShell("input keyevent 4")
                                    break
                                
                                if upload == True:
                                    # upload avatar
                                    up_avt = False
                                    self.dict_data.update({'code': 100, 'status': 'Đang upload avatar'})
                                    self.sendDataUpMainScreen.emit(self.dict_data)
                                    up_avt = self.upAvatar(self.folder_image)
                                    if up_avt:
                                        for t in range(15, -1, -1):
                                            self.dict_data.update({'code': 100, 'status': f'Chờ {t} giây để tiktok load avatar ...'})
                                            self.sendDataUpMainScreen.emit(self.dict_data)
                                            sleep(1)

                                # lấy username cá nhân
                                self.adb.runShell("input swipe 588 300 577 1600 100") # vuốt lên đầu
                                self.dict_data.update({'code': 100, 'status': 'Đang lấy username cá nhân'})
                                self.sendDataUpMainScreen.emit(self.dict_data)
                                for _ in range(2):
                                    username = self.getUsername()
                                    print(self.row, username)
                                    if 'tiktok' in username:
                                        self.adb.runShell("input keyevent 4")
                                    else: break
                                if username != False and len(username) > 4:
                                    self.dict_data.update({'code': 100, 'status': f'Đang cấu hình username: {username}'})
                                    self.sendDataUpMainScreen.emit(self.dict_data)
                                    for _ in range(2):
                                        g_captcha_result = bypassCaptcha(self.apikey1st)
                                        if g_captcha_result == False:
                                            self.dict_data.update({'code': 100, 'status': f'Giải captcha thất bại.'})
                                            self.sendDataUpMainScreen.emit(self.dict_data)
                                            continue
                                        add = self.tds.cauHinhTds(g_captcha_result, username, self.usertds, self.pwdtds)
                                        if add: break
                                        else: sleep(10)

                                    if add:
                                        check = True
                                        self.dict_data.update({'code': 200, 'user_tiktok': username, 'status': f'Cấu hình thành công: {username}'})
                                        self.sendDataUpMainScreen.emit(self.dict_data)
                                    else:
                                        upload = True
                                        sleep(5)
                                    break 
                                else:
                                    self.adb.runShell("input keyevent 4")
                                    sleep(3)
                                    self.adb.runShell("input keyevent 4")
                                    sleep(3)
                                    self.adb.runShell("input keyevent 4")
                                break
                        else:
                            self.adb.find_image('img\\tuchoi_8.png', 1, row=self.row)
                            self.adb.find_image('img\\tuchoi9.png', 1, row=self.row)
                            self.adb.clicks(166, 135, 1) # Bỏ qua đặt tên
                            self.adb.runShell("input keyevent 4")
                            sleep(3)
                            self.adb.runShell("input keyevent 4")
                            sleep(3)
                            self.adb.runShell("input keyevent 4")
                            continue

                        if check: break

                    # end for
                # end if  
                
                # run tds
                list_nv = ['tiktok_like', 'tiktok_follow'] # tiktok_comment
                self.data_like = {'cache': 0, 'data': []}
                while check and self.session == 'OK':
                    self.tds = API_TDS(self.access_token)
                    prx = self.tds.checkProxy() # get proxy
                    for _ in range(20):
                        # type_get_job = random.choices(list_nv, weights=[0.6, 0.4])[0]
                        type_get_job = 'tiktok_follow'
                        try:
                            self.dict_data.update({'code': 100, 'status': f'Đang tìm job {type_get_job}'})
                            self.sendDataUpMainScreen.emit(self.dict_data)
                            
                            if type_get_job == 'tiktok_follow' or (type_get_job == 'tiktok_like' and len(self.data_like['data']) == 0):
                                response = self.tds.getJobTds(type_get_job, prx)
                                if not response: 
                                    sleep(random.randint(2, 5))
                                    continue
                                # if type_get_job == 'tiktok_like':
                                #     try:
                                #         type_get_job = 'tiktok_follow'
                                #         response['error']
                                #         response = self.tds.getJobTds(type_get_job, prx)
                                #     except:
                                #         self.data_like = response
                            else:
                                response = self.data_like
                            
                            # print(response)
                            cache = response['cache']
                            idjob = response['data'][0]['id']
                            link = response['data'][0]['link']
                            if cache < 14:
                                if type_get_job == 'tiktok_follow':
                                    urljob = 'snssdk1180://user/profile/'+response['data'][0]['real_id']
                                    namejob = response['data'][0]['uniqueID']
                               
                                    self.dict_data.update({'code': 100, 'status': f'Đang follow user: {namejob}'})
                                    self.sendDataUpMainScreen.emit(self.dict_data)
                                    self.adb.runShell(f"am start -a android.intent.action.VIEW -d {urljob}")
                                    self.adb.runShell("settings put system accelerometer_rotation 0")
                                    sleep(4)
                                    if self.adb.find_image('img\\follow8.png', 5, row=self.row):
                                        pass
                                    # Lỗi App thì vào fl theo search user
                                    else:
                                        self.dict_data.update({'code': 100, 'status': f'Đang tìm kiếm user: {namejob}'})
                                        self.sendDataUpMainScreen.emit(self.dict_data)
                                        self.adb.runShell("am force-stop com.ss.android.ugc.trill")
                                        self.adb.runShell("monkey -p com.ss.android.ugc.trill -c android.intent.category.LAUNCHER 1")
                                        self.adb.runShell("settings put system accelerometer_rotation 0")
                                        sleep(7)
                                        for _ in range(4):
                                            self.adb.find_image('img\\closequa8.png', 1, threshold=0.6, row=self.row)
                                            self.adb.find_image('img\\tuchoi_8.png', 1, row=self.row)
                                            self.adb.find_image('img\\tuchoi9.png', 1, row=self.row)
                                            self.adb.find_image('img\\kcp.png', 1, threshold=0.7, row=self.row)
                                            if self.adb.find_image('img\\timkiem.png', 3, click=False, row=self.row):
                                                sleep(1)
                                                self.adb.send_keys(namejob) 
                                                sleep(1)
                                                self.adb.runShell("input keyevent 66") # enter
                                                sleep(3)
                                                if self.adb.find_image('img\\follow_small_8.png', 2, row=self.row):
                                                    break
                                                elif self.adb.find_image('img\\dangfollow.png', 2, click=False, row=self.row):
                                                    break
                                            self.adb.find_image('img\\chapnhantiktok.png', 1, screenshot=False, row=self.row)
                                            self.adb.runShell("input keyevent 4")
                                            sleep(3)
                                            self.adb.runShell("input keyevent 4")
                                            sleep(3)
                                            self.adb.runShell("input keyevent 4")
                                            sleep(3)
                                            self.adb.runShell("input keyevent 4")
                                            sleep(3)
                                            self.adb.clicks(1003, 135, 1) # Click kính lúp
                                elif type_get_job == 'tiktok_like':
                                    self.dict_data.update({'code': 100, 'status': f'Đang thích video: {idjob}'})
                                    self.sendDataUpMainScreen.emit(self.dict_data)
                                    self.adb.runShell(f"am start -a android.intent.action.VIEW -d {link}")  
                                    sleep(random.randint(3, 7))

                                    size = self.adb.getvmSize()
                                    x = int(size[0]) / 2
                                    y = int(size[1]) / 2
                                    self.adb.doubleClick(x, y)
                                    self.data_like['data'].pop(0)

                                self.adb.runShell("input keyevent 4")
                                self.adb.find_image('img\\tuchoi_8.png', 1, row=self.row)
                                self.adb.find_image('img\\tuchoi9.png', 1, row=self.row)
                                self.event = Event()
                                my_thread = Thread(target=self.interactTiktok)
                                my_thread.start()

                                delay = random.randint(int(self.dlMin), int(self.dlMax))
                                for t in range(delay, -1, -1):    
                                    self.dict_data.update({'code': 100, 'status': f'Chờ {t} giây để hoàn thành'})
                                    self.sendDataUpMainScreen.emit(self.dict_data)
                                    sleep(1)

                                self.event.set()
                                my_thread.join()

                                # Duyệt Job
                                self.dict_data.update({'code': 100, 'status': 'Đang check cache job'})
                                self.sendDataUpMainScreen.emit(self.dict_data)
                                if type_get_job == 'tiktok_follow':
                                    cache_job = 'TIKTOK_FOLLOW_CACHE'
                                elif type_get_job == 'tiktok_like':
                                    cache_job = 'TIKTOK_LIKE_CACHE'
                                response = self.tds.checkCacheJob(cache_job, idjob, prx)
                                if not response: continue # check cache lỗi 
                                cache = response['cache']
                                self.data_like.update({'cache': cache})

                            self.dict_data.update({'code': 100, 'cache': cache, 'status': f'Đã hoàn thành {cache} nhiệm vụ {type_get_job}.'})
                            self.sendDataUpMainScreen.emit(self.dict_data)
                            if cache >= 13: # 13 job nhận xu 1 lần
                                try:
                                    self.dict_data.update({'code': 100, 'status': f'Đang nhận xu'})
                                    self.sendDataUpMainScreen.emit(self.dict_data)
                                    if type_get_job == 'tiktok_follow':
                                        type_api = 'TIKTOK_FOLLOW&id=TIKTOK_FOLLOW_API'
                                    elif type_get_job == 'tiktok_like':
                                        type_api = 'TIKTOK_LIKE&id=TIKTOK_LIKE_API' 
                                    response1 = self.tds.submitJobFollow(type_api, prx)
                                    print(self.row, response1)
                                    if not response1: continue

                                    if response1['data']['job_success'] <= 2:
                                        xu_them = response1['data']['xu_them']
                                        total_xu_them += xu_them
                                        xumotacc += xu_them
                                        self.dict_data.update({'code': 100, 'status': f'Lỗi nhận xu: {response1["data"]["msg"]}'})
                                        self.sendDataUpMainScreen.emit(self.dict_data)
                                        
                                        print(f"{self.row} : nhanxuloi : {nhanxuloi}")
                                        nhanxuloi += 1
                                        formatted_xu = '{:,}'.format(int(xumotacc))
                                        
                                        check = False
                                        self.session = 'FAIL'
                                        self.dict_data.update({'code': 200, 'session': self.session, 'user_tiktok': '', 'cache': '0', 'status': f'Thoát tài khoản >> {username} >> đã bú: {formatted_xu}'})
                                        self.sendDataUpMainScreen.emit(self.dict_data)
                                        sleep(1)
                                        if self.getMail == 'file':
                                            with open(f'data\\mail\\stream\\{self.folder}\\acc.txt', 'a+', encoding='utf-8') as file:
                                                file.write(f"{gmail}|{username}|{formatted_xu}\n")
                                        else:
                                            with open(f'data\\mail\\acc.txt', 'a+', encoding='utf-8') as file:
                                                file.write(f"{self.row}|{gmail}|{username}|{formatted_xu}\n")
                                        break
                                    else:
                                        xu_them = response1['data']['xu_them']
                                        total_xu_them += xu_them
                                        xumotacc += xu_them
                                        formatted_number = '{:,}'.format(int(total_xu_them))
                                        xu_total = str('{:,}'.format(int(response1["data"]["xu"])))
                                        self.dict_data.update({
                                            'code': 200, 
                                            'cache': '0',
                                            'xu': xu_total, 
                                            'xuhnay': str(formatted_number), 
                                            'status': f'{type_get_job}: username: {username} nhận thành công: {response1["data"]["msg"]}'
                                            })
                                        self.sendDataUpMainScreen.emit(self.dict_data)
                                        sleep(1)
                                        nhanxuloi = 0

                                        changeAcc = False
                                        if int(xu_total.replace(',', '')) >= int(self.limitXu.replace(',', '')) and int(xu_total.replace(',', '')) <= int(self.limitXu.replace(',', ''))+200000:
                                            changeAcc = True
                                        elif int(xu_total.replace(',', '')) >= int(self.limitXu.replace(',', ''))*2 and int(xu_total.replace(',', '')) <= int(self.limitXu.replace(',', ''))*2+200000:
                                            changeAcc = True
                                        elif int(xu_total.replace(',', '')) >= int(self.limitXu.replace(',', ''))*3 and int(xu_total.replace(',', '')) <= int(self.limitXu.replace(',', ''))*3+200000:
                                            changeAcc = True

                                        # change account 
                                        if changeAcc == True:
                                            with open('data\\account_done.txt', 'a', encoding='utf-8') as save:
                                                save.write(f"{self.usertds}|{self.pwdtds}|{xu_total}\n")
                                            for _ in range(5):
                                                self.usertds = randStr(8)+str(random.randint(100, 999))
                                                self.pwdtds  = randStr(8)
                                                g_captcha_result = bypassCaptcha(self.apikey1st)
                                                new_username = self.tds.regTds(g_captcha_result, self.usertds, self.pwdtds)
                                                if new_username == False:
                                                    continue
                                                self.dict_data.update({'code': 200, 'usertds': self.usertds, 'pwdtds': self.pwdtds, 'xu': 0, 'status': f'Tài khoản đã được {xu_total} xu, thay đổi qua tài khoản {new_username}'})
                                                self.sendDataUpMainScreen.emit(self.dict_data)
                                                break
                                            
                                            # Check tds
                                            getAccount = API_TDS().getTokenTds(self.usertds, self.pwdtds)
                                            print(self.row, getAccount)
                                            if getAccount == {}:
                                                self.dict_data.update({'code': 204, 'status': 'Sai tài khoản / mật khẩu'})
                                                return self.sendDataUpMainScreen.emit(self.dict_data)
                                            self.access_token = getAccount['access_token']
                                            xu = getAccount['xu']
                                            self.tds = API_TDS(self.access_token)
                                            
                                            # cấu hình 
                                            self.dict_data.update({'code': 100, 'status': f'Đang cấu hình username: {username}'})
                                            self.sendDataUpMainScreen.emit(self.dict_data)
                                            g_captcha_result = bypassCaptcha(self.apikey1st)
                                            add = self.tds.cauHinhTds(g_captcha_result, username, self.usertds, self.pwdtds)
                                            print(add)
                                            if add: 
                                                self.dict_data.update({'code': 200, 'user_tiktok': username, 'status': f'Cấu hình thành công: {username}'})
                                                self.sendDataUpMainScreen.emit(self.dict_data)
                                                break

                                except Exception as bug: 
                                    tb = traceback.format_exc()
                                    print("Exception 2", tb)

                        except:
                            tb = traceback.format_exc()
                            print("Exception 2", tb)
                            self.dict_data.update({'code': 100, 'status': f'Lỗi lấy job {type_get_job}'})
                            self.sendDataUpMainScreen.emit(self.dict_data)
                            sleep(5)
                    
                    self.adb.runShell("am force-stop com.ss.android.ugc.trill")
                    self.dict_data.update({'code': 100, 'status': f'Thoát app vào lại'})
                    self.sendDataUpMainScreen.emit(self.dict_data)
            except:
                tb = traceback.format_exc()
                with open('report_bug\\bug_requests.txt', 'a+', encoding='UTF-8') as file:
                    file.write(f"Thread: {self.row} : {tb}\n\n")
            sleep(5)

    def interruptible_sleep(self, seconds, event):
        for _ in range(seconds):
            if event.is_set():
                break
            sleep(1)
    def interactTiktok(self):
        while not self.event.is_set():
            self.adb.runShell("input swipe 224 1435 143 285 100") # lướt
            self.interruptible_sleep(random.randint(3, 7), self.event)
            if self.event.is_set(): break
            tt = random.randint(0, 1)
            if tt == 1:
                size = self.adb.getvmSize()
                x = int(size[0]) / 2
                y = int(size[1]) / 2
                self.adb.doubleClick(x, y)
                self.interruptible_sleep(random.randint(2, 5), self.event)
                if self.event.is_set(): break
                self.adb.runShell("input keyevent 4")
            if self.event.is_set(): break
            self.interruptible_sleep(random.randint(3, 7), self.event)
            if self.event.is_set(): break
            self.adb.runShell("input keyevent 4")
    def clearDataTiktok(self):
        # for _ in range(20):
        self.adb.runShell("am force-stop com.ss.android.ugc.trill")
        result = self.adb.runShell("pm clear com.ss.android.ugc.trill")
        if result.strip() == "Success":
            self.dict_data.update({'code': 100, 'status': 'Xóa data tiktok thành công'})
            self.sendDataUpMainScreen.emit(self.dict_data)
            return True
    def VPNHMA(self, change=False, off=False):
        for _ in range(5):
            sleep(5)
            if self.adb.find_image('img\\on_8.png', 3, click=False, row=self.row):
                if off:
                    self.adb.find_image('img\\on_8.png', 3, row=self.row)
                if change:
                    self.adb.find_image('img\\rote_8.png', 3, row=self.row)
                break
            else:
                if off: break
                self.adb.find_image('img\\off_8.png', 3, row=self.row)
                break
    def VPNS1111(self, change=False, off=False):
        for _ in range(5):
            sleep(5)
            if self.adb.find_image('img\\off_1111_8.png', 3, click=False, row=self.row):
                if off: 
                    self.adb.find_image('img\\off_1111_8.png', 3, row=self.row)
                    sleep(2)
                    self.adb.clicks(427, 1220, 1)
                if change:
                    self.adb.find_image('img\\on_1111_8.png', 3, row=self.row)
                break
            else:
                if off: break
                self.adb.find_image('img\\on_1111_8.png', 3, row=self.row)
                break
    def VPN_SS(self, change=False, off=False):
        for _ in range(5):
            sleep(5)
            if self.adb.find_image('img\\onvpnss.png', 2, click=False, row=self.row):
                if off:
                    self.adb.find_image('img\\onvpnss.png', 2, row=self.row)
                if change:
                    self.adb.find_image('img\\onvpnss.png', 2, row=self.row)
                    continue
                break
            elif self.adb.find_image('img\\offvpnss.png', 2, click=False, row=self.row):
                if off: break
                self.adb.find_image('img\\offvpnss.png', 2, row=self.row)
                break
            else:
                self.adb.runShell("monkey -p com.opera.max.global -c android.intent.category.LAUNCHER 1")
    def muaMail(self):
        try:
            orderId = requests.get(f'https://taphoammo.net/api/buyProducts?kioskToken={self.keyShop}&userToken={self.apiKeyTaphoa}&quantity=1', timeout=10).json()['order_id']
            sleep(2)
            getMail = requests.get(f'https://taphoammo.net/api/getProducts?orderId={orderId}&userToken={self.apiKeyTaphoa}', timeout=10).json()['data'][0]['product']
            return getMail
        except:
            sleep(10)
            return self.muaMail()
    def duplicateFilter(self):
        file = open(f'data\\mail\\stream\\{self.folder}\\gmail_done.txt', 'w', encoding='utf-8')
        dup_fill = list(set(self.arr_gmail_done))
        for mail in dup_fill:
            file.write(mail.strip()+'\n')
        file.close()
        return dup_fill
    def changeVPN(self, change, off):
        if self.vpn == 'hma':
            self.adb.runShell("monkey -p com.hidemyass.hidemyassprovpn -c android.intent.category.LAUNCHER 1")
        elif self.vpn == '1111':
            self.adb.runShell("monkey -p com.cloudflare.onedotonedotonedotone -c android.intent.category.LAUNCHER 1")
        elif self.vpn == 'ssmax':
            self.adb.runShell("monkey -p com.opera.max.global -c android.intent.category.LAUNCHER 1")
        
        if self.vpn == 'hma':
            self.VPNHMA(change, off)
        elif self.vpn == '1111':
            self.VPNS1111(change, off)
        elif self.vpn == 'ssmax':
            self.VPN_SS(change, off)
    def registerTiktok(self):
        self.dict_data.update({'code': 100, 'status': 'Tiếp tục đăng ký với Google'})
        self.sendDataUpMainScreen.emit(self.dict_data)
        if self.adb.checkXml(CountRepeat=5, element='//node[@content-desc="Tiếp tục với Google"]') == False:
            self.adb.clicks(338 , 453) # click hạ ads gg
            if self.adb.checkXml(CountRepeat=5, element='//node[@content-desc="Tiếp tục với Google"]', click=False):
                return self.registerTiktok()
            elif self.adb.find_image('img\\tuchoi_8.png', 2, row=self.row) or self.adb.find_image('img\\tuchoi9.png', 2, row=self.row):
                return 'registered'
            return False
        sleep(2)
        self.dict_data.update({'code': 100, 'status': 'Click vào gmail để tiếp tục'})
        self.sendDataUpMainScreen.emit(self.dict_data)
        self.adb.checkXml(element='//node[@resource-id="com.google.android.gms:id/account_name"]')
        
        if self.adb.checkXml(CountRepeat=10, element='//node[@text="TikTok muốn truy cập vào Tài khoản Google của bạn"]', click=False):
            self.dict_data.update({'code': 100, 'status': f'Cho phép tiktok truy cập vào gmail.'})
            self.sendDataUpMainScreen.emit(self.dict_data)
            self.adb.runShell("input swipe 224 1435 143 285 100")
            self.adb.checkXml(CountRepeat=5, element='//node[@text="Cho phép"]', Xoffsetplus=50, Yoffsetplus=50)

        self.dict_data.update({'code': 100, 'status': f'Đợi tiktok xác minh gmail.'})
        self.sendDataUpMainScreen.emit(self.dict_data)
        for _ in range(10):
            print(_)
            if self.adb.checkXml(CountRepeat=5, element='//node[@text="Ngày sinh"]'):
                self.dict_data.update({'code': 100, 'status': f'Chọn ngày sinh'})
                self.sendDataUpMainScreen.emit(self.dict_data)
                self.adb.runShell(f"input swipe 266 1663 283 1263 {random.randint(900,1100)}")
                self.adb.runShell(f"input swipe 536 1650 550 1296 {random.randint(900,1100)}")
                self.adb.runShell(f"input swipe 803 1383 813 1881 {random.randint(90,130)}") # Năm Sinh
                self.adb.runShell(f"input swipe 803 1383 813 1881 {random.randint(100,120)}") # Năm Sinh
                self.adb.runShell(f"input swipe 803 1383 813 1881 {random.randint(200,300)}") # Năm Sinh
                self.adb.runShell(f"input swipe 803 1383 813 1881 {random.randint(200,400)}") # Năm Sinh

                if self.adb.checkXml(element='//node[@text="Tiếp"]'):
                    if self.adb.find_image('img\\blockreg.png', 5, threshold=0.8, row=self.row):
                        return 'block_reg'
                    self.dict_data.update({'code': 100, 'status': f'Xác nhận tên tiktok.'})
                    self.sendDataUpMainScreen.emit(self.dict_data) 
                    c = 0
                    for _ in range(15):
                        if self.adb.checkXml(CountRepeat=1, element='//node[@text="Xác nhận"]'):
                            c += 1
                            sleep(5)
                        elif self.adb.checkXml(CountRepeat=2, element='//node[@text="Tài khoản công khai"]'):
                            self.dict_data.update({'code': 100, 'status': f'Chỉnh sửa quyền riêng tư.'})
                            self.sendDataUpMainScreen.emit(self.dict_data) 
                            self.adb.checkXml(CountRepeat=5, element='//node[@text="Chọn “Tài khoản công khai”"]')
                            sleep(4)
                            self.adb.checkXml(CountRepeat=3, element='//node[@text="OK"]')
                            sleep(5)
                            if self.adb.checkXml(CountRepeat=5, element='//node[@text="Tiếp"]'):
                                return True
                        elif self.adb.find_image('img\\blockreg.png', 1, threshold=0.8, row=self.row):
                            return 'block_reg'
                        else:
                            if c > 0: return True
                    self.adb.runShell("input keyevent 4")
                    sleep(3)
                    self.adb.runShell("input keyevent 4")
                    sleep(3)
                    self.adb.find_image('img\\dangky8.png', 5, row=self.row)
                    return self.registerTiktok()
                else:
                    self.adb.runShell("input keyevent 4")
                    sleep(3)
                    self.adb.runShell("input keyevent 4")
                    sleep(3)
                    self.adb.find_image('img\\dangky8.png', 5, row=self.row)
                    return self.registerTiktok()
            elif self.adb.find_image('img\\tieptheo8.png', 5, row=self.row):
                self.dict_data.update({'code': 100, 'status': f'Xác minh danh tính gmail.'})
                self.sendDataUpMainScreen.emit(self.dict_data)
                sleep(3)
                self.adb.runShell("input keyevent 66") # enter
                sleep(3)
                self.adb.send_keys(self.pwd_gmail)
                self.adb.runShell("input keyevent 66") # enter
                if self.adb.checkXml(CountRepeat=10, element='//node[@text="TikTok muốn truy cập vào Tài khoản Google của bạn"]', click=False):
                    self.dict_data.update({'code': 100, 'status': f'Cho phép tiktok truy cập vào gmail.'})
                    self.sendDataUpMainScreen.emit(self.dict_data)
                    self.adb.runShell("input swipe 224 1435 143 285 100")
                    self.adb.checkXml(CountRepeat=5, element='//node[@text="Cho phép"]', Xoffsetplus=50, Yoffsetplus=50)
            elif self.adb.find_image('img\\tuchoi_8.png', 2, row=self.row) or self.adb.find_image('img\\tuchoi9.png', 2, row=self.row):
                return 'registered'
            elif self.adb.find_image('img\\user_8.png', 2, click=False, threshold=0.8, row=self.row):
                return 'registered'
            
        return False
    def getUsername(self):
        self.adb.runShell("input swipe 588 300 577 1600 100") # vuốt lên đầu
        for _ in range(15):
            # if self.adb.checkXml(CountRepeat=1, element='//node[@content-desc="Hồ sơ"]'): break
            if self.adb.find_image('img\\suahoso.png', 1, click=False, row=self.row): break
            self.adb.runShell("input swipe 224 1435 143 285 100")  # lướt
        self.adb.runShell("input swipe 588 300 577 1600 100") # vuốt lên đầu
        root = html.parse(self.adb.dumXml())
        elements = root.findall(".//*[@resource-id]")
        for element in elements:
            if '@' in element.attrib['text']:
                username = element.attrib['text'].replace("@", "")
                return username
        return ''
    def upAvatar(self, folder_avater):
        self.dict_data.update({'code': 100, 'status': 'Cấp quyền bộ nhớ, di chuyển ảnh random lên máy'})
        self.sendDataUpMainScreen.emit(self.dict_data)
        self.adb.runShell('pm grant com.ss.android.ugc.trill android.permission.WRITE_EXTERNAL_STORAGE')
        self.adb.runShell('rm -r /sdcard/Pictures/*') # xóa toàn bộ ảnh 
        for _ in range(3):
            self.dict_data.update({'code': 100, 'status': 'Tải ngẫu nhiên 3 ảnh lên máy'})
            self.sendDataUpMainScreen.emit(self.dict_data)
            img_name = self.randomPictures(folder_avater)
            self.adb.device.push(folder_avater+'/'+img_name, '/sdcard/Pictures/'+img_name)
            self.adb.runShell('am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/Pictures/'+img_name) # refresh ảnh vừa up trên android
        sleep(2)

        self.dict_data.update({'code': 100, 'status': 'Tiến hành upload avatar'})
        self.sendDataUpMainScreen.emit(self.dict_data)
        self.adb.find_image('img\\suahoso.png', 2)
        self.adb.checkXml(element='//node[@text="Thay đổi ảnh"]', Xoffsetplus=100, Yoffsetplus=-100)
        sleep(2)
        self.adb.find_image('img\\chontuthuvien.png', 5, row=self.row)
        
        # get list image 
        upSuc = False
        for i in range(5):
            sleep(2)
            posList = self.adb.checkXml(CountRepeat=5, element='//node[@class="android.widget.ImageView"]', click=False, posList=True)
            if posList == False: continue
            for _ in range(len(posList)):
                self.dict_data.update({'code': 100, 'status': 'Đang tìm kiếm ảnh'})
                self.sendDataUpMainScreen.emit(self.dict_data)
                pos = posList[_]
                self.adb.clicks(int(pos[0]), int(pos[1]))
                sleep(2)
                black = self.adb.checkColor()
                if black: break
                self.adb.runShell("input keyevent 4")
            if black: 
                upSuc = True
                break
            else:
                self.adb.runShell("input swipe 224 720 143 285 100")  # lướt ảnh
        # if upSuc == False:
                
        self.dict_data.update({'code': 100, 'status': 'Xác nhận hình ảnh làm avatar'})
        self.sendDataUpMainScreen.emit(self.dict_data)
        self.adb.find_image('img\\choose_img.png', 2)
        self.adb.checkXml(CountRepeat=2, element='//node[@text="Xác nhận"]')
        sleep(3)

        check_img = self.adb.checkXml(CountRepeat=2, element='//node[@text="Thay đổi ảnh"]', click=False)
        if check_img:
            self.adb.runShell("input keyevent 4")
            return self.upAvatar(folder_avater) 
    
        up = 0
        self.dict_data.update({'code': 100, 'status': 'Lưu và đăng ảnh.'})
        self.sendDataUpMainScreen.emit(self.dict_data)
        for _ in range(2):
            if self.adb.checkXml(CountRepeat=2, element='//node[@text="Lưu & đăng" or @text="Lưu"]'): 
                up += 1
            sleep(5)
        if self.adb.checkXml(CountRepeat=30, element='//node[@text="Thay đổi ảnh"]', click=False):
            self.adb.runShell("input keyevent 4")
            if up == 0:
                return self.upAvatar(folder_avater)
        else:
            self.adb.runShell("input keyevent 4")
            self.adb.runShell("input keyevent 4")

        self.dict_data.update({'code': 100, 'status': 'Upload avatar thành công'})
        self.sendDataUpMainScreen.emit(self.dict_data)
        return True
    def randomPictures(self, folderavt):
        if os.path.exists(folderavt) == False:
            return "NO_PATH_IMAGE"
        image = random.choice(os.listdir(folderavt))
        return image
    def publicTym(self):
        pass

    def stop(self):
        self.event.set()
        self.adb.runShell("am force-stop com.ss.android.ugc.trill", check=True) # đóng tiktok
        self.adb.runShell("input keyevent 3", check=True) # về home
        self.terminate()
        self.dict_data.update({'code': 100, 'status': 'Đã dừng tool'})
        self.sendDataUpMainScreen.emit(self.dict_data)

class senXuDialog(QDialog):
    def __init__(self, user, pwd):
        super(senXuDialog, self).__init__()
        self.tds = API_TDS()
        self.user = user
        self.pwd = pwd
        layout = QVBoxLayout()
        self.QBtn = QPushButton()

        self.setWindowIcon(QtGui.QIcon('data\\display_ui\\icons\\logo_tds.png'))
        self.setWindowTitle("Chuyển xu")
        self.setFixedWidth(250)
        self.setFixedHeight(200)
        self.QBtn.clicked.connect(self.sendXu)

        self.inputUsernhan = QPlainTextEdit()
        self.inputUsernhan.setPlaceholderText("Nhập tên người nhận")
        layout.addWidget(self.inputUsernhan)

        self.inputXunhan = QPlainTextEdit()
        self.inputXunhan.setPlaceholderText("Nhập số xu muốn chuyển (fee 10%)")
        layout.addWidget(self.inputXunhan)

        self.QBtn.setText("Chuyển xu")
        layout.addWidget(self.QBtn)
        self.setLayout(layout)

    def sendXu(self):
        self.QBtn.setText("Đang chuyển, đợi tí ...")
        self.usernhan = self.inputUsernhan.toPlainText()
        self.xusend = self.inputXunhan.toPlainText()
        send = self.tds.sendXu(self.user, self.pwd, self.usernhan, self.xusend)
        if send == 3 or send == '3':
            send = f"Chuyển thành công {self.xusend} xu cho user {self.usernhan}"
        self.QBtn.setText("Chuyển xu")
        Information(send)

class updateData(QDialog):
    def __init__(self, uic, list_row, list_id):
        super(updateData, self).__init__()
        self.QBtn = QPushButton()
        layout = QVBoxLayout()
        self.db = MONGO_DB()
        self.uic_update = uic
        self.list_row = list_row
        self.list_object_id = list_id

        self.setWindowIcon(QtGui.QIcon('data\\display_ui\\icons\\update.png'))
        self.setWindowTitle("Cập nhật dữ liệu")
        self.setFixedWidth(550)
        self.setFixedHeight(300)
        self.QBtn.clicked.connect(self.updateDuLieu)

        self.ddinput = QComboBox()
        self.ddinput.setToolTip("Dữ liệu cập nhật")
        self.ddinput.addItem("User|Pass")
        self.ddinput.addItem("Device")
        self.ddinput.addItem("Username")
        self.ddinput.addItem("Password")
        layout.addWidget(self.ddinput)

        self.input = QPlainTextEdit()
        self.input.setPlaceholderText("Nhập dữ liệu")
        layout.addWidget(self.input)

        self.QBtn.setText("Cập nhật")
        layout.addWidget(self.QBtn)
        self.setLayout(layout)
    def columnUpdate(self, dinhDang):
        column = ''
        key = ''
        if dinhDang == 'User|Pass':
            column = [8, 9]
        elif dinhDang == 'Device':
            key = 'device'
            column = 5
        elif dinhDang == 'Username':
            key = 'usertds'
            column = 8
        elif dinhDang == 'Password':
            key = 'pwdtds'
            column = 9
        return {
            'column': column,
            'key': key
        }
    def setColorStatusTable(self, row, column, status='', center=True):
        item = QTableWidgetItem(str(status))
        item.setForeground(QColor(84, 110, 122))
        if center: item.setTextAlignment(Qt.AlignCenter)
        self.uic_update.tablewidget_page.setItem(row, column, item)
    def updateDuLieu(self):
        dinhDang = self.ddinput.itemText(self.ddinput.currentIndex())
        dataUpdate = self.input.toPlainText().split('\n')
        if len(dataUpdate) < len(self.list_row):
            Information("Dữ liệu đầu vào không được bé hơn số tài khoản được chọn.")
        value = self.columnUpdate(dinhDang)
        column = value['column']
        key = value['key']
        for i in range(len(self.list_row)):
            row = self.list_row[i]
            object_id = self.list_object_id[i]
            if key == '':
                data = dataUpdate[i]
                try:
                    usertds = data.split('|')[0]
                    pwdtds = data.split('|')[1]
                except:
                    return Information("Sai định dạng đầu vào")
                self.setColorStatusTable(row, column[0], usertds)
                self.setColorStatusTable(row, column[1], pwdtds)
                dict_update = {
                    'usertds': usertds,
                    'pwdtds': pwdtds
                }
                self.db.updateOneAccount(object_id, dict_update)
            else:
                value = dataUpdate[i]
                self.setColorStatusTable(row, column, value)
                self.db.updateOneAccount(object_id, {key: value})
        Information(f"Cập nhật thành công {len(self.list_row)} dữ liệu.")
        self.close()

class changPwdDialog(QDialog):
    def __init__(self, uic, list_row, list_id):
        super(changPwdDialog, self).__init__()
        self.tds = API_TDS()
        self.db = MONGO_DB()
        self.uic_change = uic
        self.list_row = list_row
        self.list_object_id = list_id
        layout = QVBoxLayout()
        self.QBtn = QPushButton()
        self.label = QLabel()

        self.setWindowIcon(QtGui.QIcon('data\\display_ui\\icons\\logo_tds.png'))
        self.setWindowTitle("Thay đổi mật khẩu")
        self.setFixedWidth(320)
        self.setFixedHeight(200)
        self.QBtn.clicked.connect(self.changePassword)

        self.inputChange = QPlainTextEdit()
        self.inputChange.setPlaceholderText("Nhập mật khẩu muốn đổi")
        layout.addWidget(self.inputChange)

        self.QBtn.setText(f"Đổi mật khẩu cho {len(self.list_row)} tài khoản")
        layout.addWidget(self.QBtn)

        self.label.setText("")
        layout.addWidget(self.label)

        self.setLayout(layout)
    def setColorStatusTable(self, row, column, status='', center=True):
        item = QTableWidgetItem(str(status))
        item.setForeground(QColor(84, 110, 122))
        if center: item.setTextAlignment(Qt.AlignCenter)
        self.uic_change.tablewidget_page.setItem(row, column, item)
    def changePassword(self):
        result_event = threading.Event()
        result_change = None
        succ = 0
        err = 0
        newpass = self.inputChange.toPlainText().strip()
        def changePwdTds(usertds, pwdtds, newpass):
            nonlocal result_change
            result_change = self.tds.changePass(usertds, pwdtds, newpass)
            result_event.set()
        for i in range(len(self.list_row)):
            row = self.list_row[i]
            object_id = self.list_object_id[i]
            usertds = self.uic_change.tablewidget_page.item(row, 8).text()
            pwdtds = self.uic_change.tablewidget_page.item(row, 9).text()

            self.label.setText(f"Success: {succ}, Failed: {err}, Pending: {i+1}/{len(self.list_row)} account ...")

            Thread(target=changePwdTds, args=(usertds, pwdtds, newpass, )).start()
            result_event.wait()
            if result_change == True:
                succ += 1
                self.setColorStatusTable(row, 9, newpass)
                self.db.updateOneAccount(object_id, {'pwdtds': newpass})
            else:
                err += 1
        self.label.setText(f"Success: {succ}, Failed: {err}, Done: {i+1}/{len(self.list_row)} account")

# center check box in table
class CheckBoxStyle(QProxyStyle):
    def subElementRect(self, element, option, widget=None):
        r = super().subElementRect(element, option, widget)
        if element == QStyle.SE_ItemViewItemCheckIndicator:
            r.moveCenter(option.rect.center())
        return r
# set color in table
class ColorDelegate(QStyledItemDelegate):
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        # change highlight color of cells in table
        color = QColor(30, 136, 229 )
        option.palette.setColor(QPalette.Highlight, color)
        QStyledItemDelegate.paint(self, painter, option, index)
        QStyledItemDelegate.paint(self, painter, option, index)
        # Hide the border of the selected cell in qtablewidget
        itemOption = QtWidgets.QStyleOptionViewItem(option)
        if option.state & QtWidgets.QStyle.State_HasFocus:
            itemOption.state = itemOption.state ^ QtWidgets.QStyle.State_HasFocus
        super().paint(painter, itemOption, index)

class TransparentComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setStyleSheet("QComboBox { background-color: rgba(255, 255, 255, 100); }")
        
app = QApplication(sys.argv)
if(QDialog.Accepted):
    window = MainWindow()
    # sys.excepthook = my_excepthook
    window.show()
try:
    sys.exit(app.exec_())
except SystemExit:
    print('Closing Window...')