from binascii import unhexlify

import rsa

import database.get_things
from modules.secure import UserDb
from prom_db import PromDb


# Obsolete
def verify_report(report_uri):
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


def graph_comparison(g1, g2):

    in_first = []
    in_second = []
    for sub, pred, obj in g1:
        in_first.append({sub + ' ' + pred + ' ' + obj})
    for sub, pred, obj in g2:
        in_second.append({sub + ' ' + pred + ' ' + obj})
    diff_first = [x for x in in_first if x not in in_second]
    diff_second = [x for x in in_second if x not in in_first]
    difference = diff_first + diff_second
    return diff_first, diff_second, difference


def verify_fuseki_report(report_uri):
        prom_db = PromDb()
        d_report = prom_db.find(report_uri)
        if d_report:
            try:
                userid = d_report['creator']
                user_db = UserDb()
                user = user_db.find(userid)
                publickey = user['publickey']
                pub_key = rsa.PublicKey.load_pkcs1(publickey) # retrieve back a key object
                report_in_db = d_report['report']
                report_from_fuseki  =  database.get_things.get_report_rdf(report_uri)
                signedreport = unhexlify(d_report['signed_report'])

                rsa.verify(report_in_db, signedreport, pub_key)

                from rdflib import Graph,compare
                d_g = Graph().parse(data=report_in_db, format='n3')
                f_g = Graph().parse(data=report_from_fuseki, format='n3')
                difference = graph_comparison(d_g, f_g)

                if len(difference[0])+len(difference[1])+len(difference[2])== 0:
                    return True, 'Verification passed'
                else:
                    return False, difference
            except Exception as e:
                print e.message
                return False, e.message
        else :
            return False, 'Report cannot be found!'


if __name__ == '__main__':
    verifyFuseki("http://localhost:9000#bcb8f4ae-1e5f-4405-9cfd-87977cab8ad3")

