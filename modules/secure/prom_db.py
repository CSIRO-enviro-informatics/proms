import pymongo
import settings

class PromDb:
    def __init__(self):
        self.mongo = pymongo.MongoClient(settings.MONGODB)
        self.mongo_db = self.mongo['prov']
        self.report = self.mongo_db['report']


    def add(self, report):
        self.report.insert(report)

    def find(self, report_uri):
        result =self.report.find_one({'uri': {"$regex" : report_uri, "$options":"-i"}})

        return result

    def list(self):
        results =list(self.report.find())
        return results


if __name__ == '__main__':

    db = PromDb()
    report = {"uri":"http://localhost:9000#2e655a23-1605-470f-9508-7306a2202dfd", "md5":"123456" }
    #db.add(report)

    reports = db.list()
    print len(reports)

    report = db.find("http://localhost:9000#2e655a23-1605-470f-9508-7306a2202dfd")
    print report['md5']
