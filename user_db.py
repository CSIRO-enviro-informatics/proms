import pymongo
import settings


class UserDb:

    def __init__(self):
        self.mongo = pymongo.MongoClient(settings.MONGODB)
        self.mongo_db = self.mongo['prov']
        self.user = self.mongo_db['user']


    def new(self, user):
        self.user.insert(user.__dict__)

    def find(self, id):
        result =self.user.find_one({'id': {"$regex" : id, "$options":"-i"}})

        return result

    def list(self):
        results =list(self.user.find())
        return results


if __name__ == '__main__':

    db = UserDb()
    report = {"uri":"http://localhost:9000#2e655a23-1605-470f-9508-7306a2202dfd", "md5":"123456" }
    #db.add(report)

    reports = db.list()
    print len(reports)

    report = db.find("http://localhost:9000#2e655a23-1605-470f-9508-7306a2202dfd")
    print report['md5']
