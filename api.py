__author__ = 'bai187'


from flask import Blueprint, Response, request, redirect, render_template, g, jsonify
from prom_db import PromDb
from flask_httpauth import HTTPBasicAuth
from user import User
from user_db import UserDb
import settings
import functions
import rsa
from binascii import unhexlify,hexlify
import functions_db
from rdflib import Graph
import cStringIO

auth = HTTPBasicAuth()


api = Blueprint('api', __name__)


#
#   All the routes in the API
#
@api.app_errorhandler(404)
def page_not_found(e):
    return {"Error":e}

@api.route('/api/privatekey')
@auth.login_required
def get_privatekey():
    usr = g.user
    uid = usr.id
    privatekey =  usr.privatekey
    return privatekey

@api.route('/api/verify_signed_report/', methods=['POST'])
@auth.login_required
def verifySignedReport():

        #decrpted the message encrypted by private key
        usr = g.user
        publickey = usr.publickey
        pub_key = rsa.PublicKey.load_pkcs1(publickey) # retrieve back a key object
        report = request.form['report']
        signedreport = unhexlify(request.form['signedreport'])
        report_id = request.form.get('report_id','')
        try:
            rsa.verify(report, signedreport, pub_key)
            return jsonify({"Verified":True})
        except:
            return jsonify({"Verified":False})


@api.route('/api/register_signed_report/', methods=['POST'])
@auth.login_required
def registerSignedReport():

        #decrpted the message encrypted by private key
        usr = g.user
        publickey = usr.publickey
        pub_key = rsa.PublicKey.load_pkcs1(publickey) # retrieve back a key object
        report = request.form['report']
        signedreport = unhexlify(request.form.get('signedreport',''))
        report_id = request.form.get('report_id','')
        try:
            rsa.verify(report, signedreport, pub_key)
            # Post to fusaki server
            # rdf_g = Graph()
            # try:
            #     g_report = rdf_g.parse(cStringIO.StringIO(report), format="n3")
            #     print g_report
            # except:
            #     pass
            #
            #
            # result = functions_db.db_insert_secure_named_graph(report, report_id, True)
            # #send_pingback(g)
            #
            # if result[0]:
            #     db = PromDb()
            #     db.add({"uri":report_id,
            #             "creator":usr.id,
            #             "signed_report":signedreport}
            #     )

            db = PromDb()
            report_json = {
                            "uri":report_id,
                            "creator":usr.id,
                            "report":report,
                            "signed_report":hexlify(signedreport)
                           }

            db.add(report_json)
            return {"Succeed":True}

        except Exception as e:
            print e.message
            return jsonify({"Error":e.message})





@api.route('/api/resource')
@auth.login_required
def get_resource():
    usr = g.user
    username = usr['id']
    return "Hello, " +username

@api.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

#todo complete user/password verification
@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        if User.verify_password(username_or_token, password):
            return True
        else:
            return False

    return True

@api.route('/api/get_uri_bases')
def getURIBases():

    return jsonify({
                        "report_base_URI":settings.REPORT_BASE_URI,
                        "reportingsystem_base_URI":settings.REPORTINGSYSTEM_BASE_URI,
                        "entity_base_URI":settings.ENTITY_BASE_URI,
                        "activity_base_URI":settings.ACTIVITY_BASE_URI,
                        "agent_base_URI":settings.ENTITY_BASE_URI

        })