__author__ = 'django'

import settings
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask import g,jsonify
import rsa
from base64 import b64decode
from binascii import hexlify
from user_db import UserDb


class User:
    id = ''
    username =''
    password_hash = ''
    publickey=''
    privatekey=''


    def __init__(self,userid):
        self.id = userid

    @staticmethod
    def list():
        userdb = UserDb()
        users_db = userdb.list()
        users=[]
        for user_db in users_db :
            try:
                user = User.convertedfromdb(user_db)
                users.append(user.json())
            except:
                pass


        return users



    @staticmethod
    def find(userid):
        userdb = UserDb()
        user_db = userdb.find(userid)
        if user_db:
            user = User.convertedfromdb(user_db)
            return user.json()
        else:
            return None

    @staticmethod
    def convertedfromdb(db_user):
        user = User(db_user['id'])
        user.privatekey = db_user['privatekey']
        user.publickey =db_user['publickey']
        return user

    @staticmethod
    def new(userid):

        user = User.find(userid)
        if user == None:
            user = User(userid)
            user.generate_rsa_keypairs()
            db = UserDb()
            db.new(user)
            return  User.find(userid)
        else:
            return user


    @staticmethod
    def verify_password(name, password):
        user = User.find(name)
        if user:
            g.user = user
            return True
        else:
            return False


    def generate_auth_token(self, expiration = 600):
        s = Serializer(settings.SECRET_KEY, expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(settings.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token


        uid = data['id']

        user = User.find(uid)
        if user:
            g.user = user
        return user

    #RSA
    def generate_rsa_keypairs(self):
        (pub_key, priv_key) = rsa.key.newkeys(512)
        self.publickey = pub_key.save_pkcs1()
        self.privatekey = priv_key.save_pkcs1()


    def test_rsa_keypairs(self):
        #return a pair of public key objects
        (pub_key, priv_key) = rsa.key.newkeys(512)

        crypto = rsa.encrypt('hello', pub_key)
        print crypto
        result = rsa.decrypt(crypto, priv_key)
        print result


        privatekey = priv_key.save_pkcs1() #this is the key text
        # pkey = rsa.PrivateKey.load_pkcs1(privatekey) # retrieve back a key object

        message = result

        signed_text = rsa.sign(message,priv_key,'SHA-1')
        print signed_text
        print rsa.verify(message, signed_text, pub_key)

    def json(self):
        result={}
        result['id']= self.id
        result['privatekey'] = self.privatekey
        result['publickey'] = self.publickey
        return result


if __name__ == '__main__':
    user = User.find("bai187")
    print user

    user.test_rsa_keypairs()
