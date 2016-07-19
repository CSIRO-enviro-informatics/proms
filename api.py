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
import sys
from rules_proms.proms_basic_report_ruleset import PromsBasicReportValid
from rules_proms.proms_internal_report_ruleset import PromsInternalReportValid
from rules_proms.proms_external_report_ruleset import PromsExternalReportValid
from rules_proms.proms_reporting_system_ruleset import PromsReportingSystemValid



auth = HTTPBasicAuth()


api = Blueprint('api', __name__)


#
#   All the routes in the API
#
@api.app_errorhandler(Exception)
def api_runtime_exception(e):
    print e
    return jsonify({"error":e.message})

@api.route('/api/errortest')
def error_test():
    raise Exception("It is a test")


@api.route('/api/newuser')
def newuser():
    userid = request.headers.get('user')
    if userid:
        user = User.new(userid)
        return jsonify(user)
    else:
        return jsonify({"Error":"User id needs to be in HTTP Header"})


@api.route('/api/privatekey')
@auth.login_required
def get_privatekey():
    usr = g.user
    uid = usr['id']
    privatekey =  usr['privatekey']
    return privatekey

@api.route('/api/verify_signed_report/', methods=['POST'])
@auth.login_required
def verifySignedReport():

        #decrpted the message encrypted by private key
        usr = g.user
        publickey = usr['publickey']
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
        publickey = usr['publickey']
        pub_key = rsa.PublicKey.load_pkcs1(publickey) # retrieve back a key object
        report = request.form['report']
        signedreport = unhexlify(request.form.get('signedreport',''))
        #obsolete
        report_id = request.form.get('report_id','')
        try:
            rsa.verify(report, signedreport, pub_key)
            # Post to fusaki server
            rdf_g = Graph()

            g_report = rdf_g.parse(cStringIO.StringIO(report), format="n3")
            print g_report

            # Report validation (Basic, Internal and External)
            report_type = ''
            reporting_system = ''
            query = '''
                PREFIX proms: <http://promsns.org/def/proms#>
                SELECT DISTINCT ?type ?rs WHERE {
                        ?r a ?type .
                        OPTIONAL { ?r proms:reportingSystem ?rs } .
                    FILTER (?type = proms:BasicReport || ?type = proms:InternalReport || ?type = proms:ExternalReport)
                }
            '''
            result = g_report.query(query)
            if len(result) == 1:
                for row in result:
                    if len(row) > 0:
                        report_type = row[0]
                        if len(row) == 2:
                            reporting_system = row[1]
                        break
            if 'BasicReport' in report_type:
                pr = PromsBasicReportValid(g_report)
            elif 'InternalReport' in report_type:
                pr = PromsInternalReportValid(g_report)
            elif 'ExternalReport' in report_type:
                pr = PromsExternalReportValid(g_report)
            else:
                return [False, 'Unknown Report type (expecting "BasicReport", "InternalReport" or "ExternalReport")']
            conf_results = pr.get_result()
            fail_reasons = []
            for ruleset in conf_results:
                if not ruleset['passed']:
                    for rule_result in ruleset['rule_results']:
                        if not rule_result['passed']:
                            for reason in rule_result['fail_reasons']:
                                fail_reasons.append(reason)

            # Additional validation (if any, as defined in ReportingSystem)
            if reporting_system != '':
                rs_dict =functions.get_reportingsystem_dict(reporting_system)
                if 'v' in rs_dict:
                    validation_name = rs_dict['v']
                    validation_module = __import__('rules_proms.' + validation_name)
                    validation_module = getattr(validation_module, validation_name)
                    validation_method = getattr(validation_module, validation_name)
                    pr = validation_method(g)
                    conf_results = pr.get_result()
                    for ruleset in conf_results:
                        if not ruleset['passed']:
                            for rule_result in ruleset['rule_results']:
                                if not rule_result['passed']:
                                    for reason in rule_result['fail_reasons']:
                                        fail_reasons.append(reason)

            if len(fail_reasons) == 0:
                #Get Report URI
                query = '''
                    PREFIX proms: <http://promsns.org/def/proms#>
                    SELECT  ?r ?job
                    WHERE {
                      {?r a proms:Report}
                      UNION
                      {?r a proms:BasicReport}
                      UNION
                      {?r a proms:ExternalReport}
                      UNION
                      {?r a proms:InternalReport}
                      ?r proms:nativeId ?job .
                    }
                '''
                r_uri = ''
                graph_name = ''
                result = rdf_g.query(query)
                for row in result:
                    r_uri = row[0]
                    break
                if r_uri:
                    graph_name = '<' + r_uri + '>'
            else:
                return jsonify({"status":False, "error":fail_reasons[0]})
            report_id = r_uri
            result = functions_db.db_insert_secure_named_graph(report, graph_name, True)
            #send_pingback(g)

            if result[0]:
                db = PromDb()
                report_json = {
                                "uri":report_id,
                                "creator":usr["id"],
                                "report":report,
                                "signed_report":hexlify(signedreport)
                               }

                db.add(report_json)
            return jsonify({"status":result[0]})
        except:
            e = sys.exc_info()[0]
            return jsonify({"Error":e.message})

        # try:
        #     rsa.verify(report, signedreport, pub_key)
        #     db = PromDb()
        #     report_json = {
        #                     "uri":report_id,
        #                     "creator":usr['id'],
        #                     "report":report,
        #                     "signed_report":hexlify(signedreport)
        #                    }
        #
        #     db.add(report_json)
        #     return {"Succeed":True}
        # except :
        #     e = sys.exc_info()[0]
        #     return jsonify({"Error":e})





@api.route('/api/resource')
@auth.login_required
def get_resource():
    usr = g.user
    username = usr['id']
    return "Hello, " +username

@api.route('/api/token')
@auth.login_required
def get_auth_token():
    user = User(g.user['id'])
    token = user.generate_auth_token()
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