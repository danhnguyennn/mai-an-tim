from models.mongoServer import MONGO_DB
import json

with open('config\\config.json', 'r', encoding='utf-8-sig') as file:
    config = json.loads(file.read())
    version = config['version']

db = MONGO_DB()
db.addDataToDB()
db.deleColumn()
db.addColumnSetting()
print(f"Cập nhật dữ liệu database cho phiên bản {version} thành công.")
