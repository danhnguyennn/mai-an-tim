from models.adbModels import ADB_TOOL
from time import sleep

row = 'test'
adb = ADB_TOOL('52001ee6ec527457')


# adb.runShell("input swipe 224 720 143 285 100")  # lướt
# for _ in range(5):
# posList = adb.checkXml(CountRepeat=1, element='//node[@text="Bỏ qua"]', click=False)
# print(posList)
# print(posList)
#     if posList != False: break
# for _ in range(len(posList)):
#     dict_data.update({'code': 100, 'status': 'Đang tìm kiếm ảnh'})
#     sendDataUpMainScreen.emit(dict_data)
#     pos = posList[_]
#     adb.clicks(int(pos[0]), int(pos[1]))
#     sleep(2)
#     black = adb.checkColor()
#     if black: break
#     adb.runShell("input keyevent 4")
adb.find_image('img\\tuchoi9.png', 5, row=row)

# result = adb.runShell('', type='screencap')
# with open(f"img\\screentest.png", "wb") as fp:
#     fp.write(result)