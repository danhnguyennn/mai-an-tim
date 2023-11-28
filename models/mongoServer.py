import pymongo
from bson.objectid import ObjectId

class MONGO_DB:
    def __init__(self) -> None:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        db = myclient["DataTds"]
        table_list = db.list_collection_names()
        self.accountTds = db["account"]
        self.settingTds = db["setting"]
        self.settingShow = db["settingShow"]

        if "account" not in table_list:
            dict_account = {
                'session': 'FAIL',
                'phone': 'Máy xx',
                'device': '',
                'version': '8.1.0',
                'user_tiktok': '',
                'usertds': '',
                'pwdtds': '',
                'xu': '0',
                'xuhnay': '0',
                'vpn': '1111'
            }
            self.accountTds.insert_one(dict_account)
        if "setting" not in table_list:
            dict_setting = {
                'getMail': 'api', # file # shop
                'site': 'taphoammo',
                'apiKeyTaphoa': '',
                'keyShop': '',
                'apikey1st': '',
                'path_image': '',
                'dlMin': 5,
                'dlMax': 10,
                'limitXu': {
                    'limit_xu_0': '10000000',
                    'limit_xu_1': '20000000',
                    'limit_xu_2': '30000000',
                    'limit_xu_3': '40000000',
                },
                'interactSleepAcc': True,
                'interactSleepJob': True,
                # 'timeStart': ''
                # 'timeEnd': ''
                'sleepStopAcc': 0,
                'limitStopAcc': 100,
                'sleepStopJob': 0,
                'limitStopJob': 500,
                'userShopMail': '',
                'pwdShopMail': ''
            }
            self.settingTds.insert_one(dict_setting)
        if "settingShow" not in table_list:
            dict_show = {
                'session': False,
                'name_phone': True,
                'version': True,
                'device': True,
                'unique_tiktok': True,
                'username': True,
                'password': True,
                'total': True,
                'hnay': True,
                'vpn': True,
                'timelast': True,
                'cache': True,
                'accrun': False,
                'jobday': False
            }
            self.settingShow.insert_one(dict_show)
    def getAllAccount(self):
        fields_to_include = {
            'status': 0
        }
        list_account = self.accountTds.find({}, fields_to_include)
        count_account = self.accountTds.count_documents({})
        return {
            'data': list_account,
            'count': count_account
        }
    def getOneAccount(self, idObject):
        pass
    def addAccount(self, dict_account):
        add_one = self.accountTds.insert_one(dict_account)
        return add_one
    def updateOneAccount(self, idObject, data_update: dict):
        document_id = ObjectId(idObject)
        update = self.accountTds.update_one({"_id": document_id}, {'$set': data_update})
        return update
    def deleteAccount(self, idObject):
        document_id = ObjectId(idObject)
        delete = self.accountTds.delete_one({"_id": document_id})
        if delete.deleted_count == 1:
            return True
        return False
    def addDataToDB(self):
        update_criteria = {}
        update_data = {'$set': {'vpn': '1111'}}
        self.accountTds.update_many(update_criteria, update_data)
    
    # table setting 
    def getSetting(self):
        dict_setting = self.settingTds.find_one()
        return dict_setting
    def updateSetting(self, new_dict_setting):
        update_setting = self.settingTds.update_one({}, {'$set': new_dict_setting})
        return update_setting
    def deleColumn(self):
        column_to_remove = 'vpn'
        self.settingTds.update_many({}, {'$unset': {
            "vpn": "",
            "stopSleep": ""
        }})
    def addColumnSetting(self):
        update_criteria = {}
        update_data = {'$set': {
            'limitXu': {
                'limit_xu_0': '10000000',
                'limit_xu_1': '20000000',
                'limit_xu_2': '30000000',
                'limit_xu_3': '40000000',
            },
            'sleepStopAcc': 0,
            'interactSleepAcc': True,
            'interactSleepJob': True,
            'sleepStopJob': 0,
            'limitStopJob': 500,
            'userShopMail': '',
            'pwdShopMail': ''
            }}
        self.settingTds.update_many(update_criteria, update_data)

    # table column show
    def getSettingShow(self):
        dict_setting = self.settingShow.find_one()
        return dict_setting
    def updateSettingShow(self, new_setting_show):
        update_setting = self.settingShow.update_one({}, {'$set': new_setting_show})
        return update_setting

    # _del_
    def resetStatusAccount(self):
        self.accountTds.update_many(
            {'status': 'RUN'}, {'$set': {'status': "OK"}})

# MONGO_DB().getAllAccount()