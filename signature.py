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
    verifyFuseki("http://localhost:9000#bcb8f4ae-1e5f-4405-9cfd-87977cab8ad3")

