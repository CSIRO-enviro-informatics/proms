__author__ = 'django'
from prom_db import PromDb
from user_db import UserDb
import rsa
from binascii import unhexlify,hexlify
import functions


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

def graphComparison(g1, g2):
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

def verifyFuseki(report_uri):
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
                report_from_fuseki  =  functions.get_report_rdf(report_uri)
                signedreport = unhexlify(d_report['signed_report'])

                from rdflib import Graph,compare
                d_g = Graph().parse(data=report_in_db, format='n3')
                f_g = Graph().parse(data=report_from_fuseki, format='n3')

                diff_first, diff_second, difference = graphComparison(d_g, f_g)
                #print'Diff first : ' + str(diff_first)
                #print'Diff second: ' + str(diff_second)
                #print'Difference : ' + str(difference)
                if len(difference)==0:
                    print 'Graphs are same'
                else:
                    print 'Graphs are different'

                # import graphcomparision
                # n_quads1 = graphcomparision.make_authorititive_serialisation_of_graph(d_g, report_uri)
                # n_quads2 = graphcomparision.make_authorititive_serialisation_of_graph(f_g, report_uri)

                from rdflib import Graph,compare
                # d_g_1 = Graph().parse(data=n_quads1, format='n3')
                # f_g_2 = Graph().parse(data=n_quads2, format='n3')
                same = compare.isomorphic(d_g,f_g)
                print same



                rsa.verify(report_in_db, signedreport, pub_key)
                return True, 'Certified!'
            except Exception as e:
                print e.message
                return False, e.message
        else :
            return False, 'Report cannot be found!'

if __name__ == '__main__':
    verifyFuseki("http://localhost:9000#19f92331-eaf6-40a3-b0c3-291a45d98db9")

