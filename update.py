from models.mongoServer import MONGO_DB

db = MONGO_DB()
db.addDataToDB()
db.deleColumn()
db.addColumnSetting()
print("Cập nhật dữ liệu database cho phiên bản 1.1.1.7 thành công.")