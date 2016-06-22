__author__ = 'django'
from prom_db import PromDb
from user_db import UserDb
import rsa
from binascii import unhexlify,hexlify


def verifyReport(report_uri):
        prom_db = PromDb()
        d_report = prom_db.find(report_uri)
        if d_report:
            try:
                userid = d_report['creator']
                user_db = UserDb()
                user = user_db.find(userid)
                publickey = user['publickey']
                pub_key = rsa.PublicKey.load_pkcs1(publickey) # retrieve back a key object
                report = d_report['report']
                signedreport = unhexlify(d_report['signed_report'])

                rsa.verify(report, signedreport, pub_key)
                return True, 'Certified!'
            except Exception as e:
                return False, e.message
        else :
            return False, 'Report cannot be found!'
