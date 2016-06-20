__author__ = 'bai187'


from flask import Blueprint, Response, request, redirect, render_template, g, jsonify
from prom_db import PromDb
from flask_httpauth import HTTPBasicAuth
from user import User
import settings
import functions
import rsa
from binascii import unhexlify

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

@api.route('/api/signedreport/', methods=['POST'])
@auth.login_required
def signedreport():

        #decrpted the message encrypted by private key
        usr = g.user
        publickey = usr.publickey
        pub_key = rsa.PublicKey.load_pkcs1(publickey) # retrieve back a key object
        report = request.form['report']
        signedreport = unhexlify(request.form['signedreport'])
        try:
            rsa.verify(report, signedreport, pub_key)
            return  jsonify({"Verified":"Succeed"})
        except:
            return jsonify({"Verified":"False"})


        # if verified:
        #     put_result = functions.put_report(report)
        #     if put_result[0]:
        #         return {"Status":"Succeed"}
        #     else:
        #         return {"Status":"Failed"}
        # else:
        #     return {"Error":"Failed to pass signature verification"}


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
