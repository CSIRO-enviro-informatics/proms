from flask import Blueprint, Response, request, redirect, render_template, g, jsonify
from prom_db import PromDb
from flask_httpauth import HTTPBasicAuth
from user import User
auth = HTTPBasicAuth()

routes = Blueprint('routes', __name__)
import functions
import functions_db
import urllib
import settings
import json
from collections import Counter
import operator


#
#   All the routes in the API
#
@routes.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@routes.route('/')
def home():
    return render_template('index.html', PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI)


@routes.route('/id/')
def ids():
    return render_template('id.html', PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI)


@routes.route('/id/reportingsystem/', methods=['GET', 'POST'])
def reportingsystem():
    if request.method == 'GET':
        if request.args.get('uri'):
            reportingsystem = functions.get_reportingsystem_dict(request.args.get('uri'))
            return render_template('reportingsystem.html',
                                       REPORTINGSYSTEM=reportingsystem)

        else:
            #if 'text/html' in request.headers.get('Accept'):
                reportingsystems=functions.get_reportingsystems_dict()
                return render_template('reportingsystem.html',
                                       REPORTINGSYSTEMS=reportingsystems,
                                       PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI)
            #else:
            #    if request.headers.get('rdf_object'):
            #        rdf_object = request.args.get('rdf_object')
            #        return Response(json.dumps(rdf_object), status_code=200, mimetype="application/rdf+json")

    #process a posted Report
    if request.method == 'POST':
        #read the incoming report
        #only accept turtle POSTS
        if 'text/turtle' in request.headers['Content-Type']:
            put_result = functions.put_reportingsystem(request.data)
            if put_result[0]:
                return Response('Inserted: ' + put_result[1], status=201, mimetype='text/plain')
            else:
                return Response('Insert failed for the following reasons:\n\n' + '\n'.join(put_result[1]), status=400, mimetype='text/plain')
        else:
            return Response('Only turtle documents allowed', status=400, mimetype='text/plain')


@routes.route('/id/report/', methods=['GET', 'POST'])
def reports():
    if request.method == 'GET':
        #single Report
        if request.args.get('uri'):
            uri = urllib.unquote(request.args.get('uri'))
            if request.args.get('_format'):
                if 'text/turtle' in request.args.get('_format') == 'text/turtle':
                    response = functions.get_report_rdf(uri)
                    return Response(response, status=201, mimetype='text/turtle', headers={"Content-Disposition": "filename=Report.ttl"})
                else:
                    return Response('Unknown format type', status=400, mimetype='text/plain')
            else:
                report = functions.get_report_dict(uri)
                import signature
                prom_db = PromDb()
                signed_report = prom_db.find(uri)

                if signed_report:
                    certified, status = signature.verifyFusekiReport(uri)
                    if certified:
                        report['verified'] = True
                        report['signedby'] = signed_report['creator']
                    else:
                        report['verified'] = False
                        report['status'] = status


                return render_template('report.html',
                                       REPORT=report,
                                       PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI)
        #multiple Reports (register)
        else:
            if request.args.get('_format'):
                return Response('A specific report URI must be provided', status=400, mimetype='text/plain')
            else:
                reports = functions.get_reports_dict()
                prom_db = PromDb()
                reportsindb = prom_db.list()
                signed_reports = [x for x in reportsindb if x.has_key('creator')]
                import signature
                for report in reports:
                    key_result = next((x for x in signed_reports if x["uri"] == report["r_u"]),None)
                    if key_result:
                        report['signedby'] = key_result['creator']

                #signed reports - Testing purpose

                for signed_report in signed_reports:
                    certified, status = signature.verifyFusekiReport(signed_report['uri'])
                    if certified:
                        signed_report['verified'] = True
                    else:
                        signed_report['verified'] = False
                        signed_report['status'] = status



                return render_template('report.html',
                                       REPORTS=reports,
                                       SIGNED_REPORTS = signed_reports,
                                       PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI)

    #process a posted Report
    if request.method == 'POST':
        #read the incoming report
        #only accept turtle POSTS
        if 'text/turtle' in request.headers['Content-Type']:
            #check report conformance and insert if ok, reporting all errors
            put_result = functions.put_report(request.data)
            if put_result[0]:
                return Response('Inserted', status=201, mimetype='text/plain')
            else:
                return Response('Insert failed for the following reasons:\n\n' + '\n'.join(put_result[1]), status=400, mimetype='text/plain')
        else:
            return Response('Only turtle documents allowed', status=400, mimetype='text/plain')


@routes.route('/id/report/<regex(".{36}"):report_id><regex("(\..{3,4})?"):extension>', methods=['GET'])
def report_id(report_id, extension):
    # we're only handling turtl & HTML docs for now
    # we forward on the accept header/_format directive or extension as an extension

    #check requested format
    if (request.headers.get('Content-Type') == 'text/turtle' or
        request.args.get('_format') == 'text/turtle' or
        extension == '.ttl'):
        new_extension = '.ttl'
    else:
        # default is HTML
        #   Content-Type' == 'text/html',
        #   _format == 'text/html'
        #   extension == '.html'
        #   extension == '.htm' ?? perhaps
        new_extension = '.html'

    return redirect('/doc/report/' + report_id + new_extension, code=303)


@routes.route('/doc/report/<regex(".{36}"):report_id><regex("(\..{3,4})?"):extension>', methods=['GET'])
def report_doc(report_id, extension):

    #check requested format
    if (request.headers.get('Content-Type') == 'text/turtle' or
        request.args.get('_format') == 'text/turtle' or
        extension == '.ttl'):

        # TODO: return turtle
        return 'report in turtle'
    """
    # TODO: Re-implement later
    else:
        # this code is the same as for /id/report/?url=X
        # TODO: de-duplicate this code
        uri = request.url
        #get back the original URI
        uri = uri.replace('/doc/', '/id/')
        uri = uri.replace(extension, '')
        html = functions.get_proms_html_header()
        html += '''
        <h1>Provenance Management Service</h1>
        <h2>A Report</h2>
        <h3>URI: ''' + uri + '''</h3>
        <p style="font-style: italic;">Under development, November, 2014.</p>
        '''
        html += functions.get_report_html(uri)
        html += functions.get_proms_html_footer()
        return Response(html, status=200, mimetype='text/html')
    """


@routes.route('/id/entity', methods=['GET'])
@routes.route('/id/entity/', methods=['GET'])
def entities():
    #single Entity
    if request.args.get('uri'):
        #unencode the uri QSA
        uri = urllib.unquote(request.args.get('uri'))
        if request.args.get('_format'):
            if 'text/turtle' in request.args.get('_format'):
                response = functions.get_entity_rdf(uri)
                return Response(response, status=201, mimetype='text/turtle', headers={"Content-Disposition": "filename=Entity.ttl"})
            else:
                return Response('Unknown format type', status=400, mimetype='text/plain')
        else:
            entity = functions.get_entity_dict(uri)
            return render_template('entity.html',
                               ENTITY=entity)
    #multiple Entities (register)
    else:
        if request.args.get('_format'):
            return Response('A specific Entity URI must be provided', status=400, mimetype='text/plain')
        else:
            entities = functions.get_entities_dict()
            return render_template('entity.html',
                               PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                               ENTITIES=entities)


@routes.route('/id/activity', methods=['GET'])
@routes.route('/id/activity/', methods=['GET'])
def activities():
    #single Activity
    if request.args.get('uri'):
        #unencode the uri QSA
        uri = urllib.unquote(request.args.get('uri'))
        if request.args.get('_format'):
            if 'text/turtle' in request.args.get('_format'):
                response = functions.get_activity_rdf(uri)
                return Response(response, status=201, mimetype='text/turtle', headers={"Content-Disposition": "filename=Activity.ttl"})
            else:
                return Response('Unknown format type', status=400, mimetype='text/plain')
        else:
            activity = functions.get_activity_dict(uri)
            return render_template('activity.html',
                                   PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                                   ACTIVITY=activity,
                                   WEB_SUBFOLDER=settings.WEB_SUBFOLDER)
    #multiple Activities (register)
    else:
        if request.args.get('_format'):
            return Response('A specific Entity URI must be provided', status=400, mimetype='text/plain')
        else:
            activities = functions.get_activities_dict()
            return render_template('activity.html',
                                   PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                                   ACTIVITIES=activities,
                                   WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


@routes.route('/id/agent/', methods=['GET'])
def agents():
    #single Agent
    if request.args.get('uri'):
        #unencode the uri QSA
        uri = urllib.unquote(request.args.get('uri'))
        if request.args.get('_format'):
            if 'text/turtle' in request.args.get('_format'):
                response = functions.get_agent_rdf(uri)
                return Response(response, status=201, mimetype='text/turtle', headers={"Content-Disposition": "filename=Agent.ttl"})
            else:
                return Response('Unknown format type', status=400, mimetype='text/plain')
        else:
            agent = functions.get_agent_dict(uri)
            return render_template('agent.html',
                                   AGENT=agent,
                                   WEB_SUBFOLDER=settings.WEB_SUBFOLDER)
    #multiple Agents (register)
    else:
        if request.args.get('_format'):
            return Response('A specific Entity URI must be provided', status=400, mimetype='text/plain')
        else:
            agents = functions.get_agents_dict()
            return render_template('agent.html',
                                   PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                                   AGENTS=agents,
                                   WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


# Deprecated - XXX Remove
@routes.route('/function/pingback', methods=['GET', 'POST'])
def pingback():
    if request.method == 'GET':
        return render_template('pingback.html',
                               WEB_SUBFOLDER=settings.WEB_SUBFOLDER)
    #process a pingback
    if request.method == 'POST':
        pass


@routes.route('/function/receive_pingback', methods=['POST'])
def receive_pingback():
    if request.method == 'GET':
        return render_template('pingback.html',
                               WEB_SUBFOLDER=settings.WEB_SUBFOLDER)
    #process a pingback
    if request.method == 'POST':
        pingback_result = functions.register_pingback(request.data)
        if pingback_result[0]:
            return Response('OK', status=200)
        else:
            return Response(pingback_result[1], status=400, mimetype='text/plain')


@routes.route('/function/sparql/', methods=['GET', 'POST'])
def sparql():
    # Query submitted
    if request.method == 'POST':
        if len(request.args) == 0:
            sd = functions.get_service_description(request)
            if sd[0]:
                if 'text/turtle' in request.headers['Content-Type']:
                    return Response(sd[1], status=200, mimetype='text/turtle')
                elif 'application/json' in request.headers['Content-Type']:
                    return Response(sd[1], status=200, mimetype='application/json')
                elif 'application/rdf' in request.headers['Content-Type']:
                    return Response(sd[1], status=200, mimetype='application/rdf')
            else:
                return Response('Error retrieving service description', status=400, mimetype='text/plain')
        query = request.form['query']
        query_result = functions_db.db_query_secure(query)
        if query_result and 'results' in query_result:
            query_result = json.dumps(query_result['results']['bindings'])
        else:
            query_result = json.dumps(query_result)
        if 'form' in request.values and request.values['form'].lower() == 'true':
            return render_template('function_sparql.html',
                                   query=query,
                                   query_result=query_result,
                                   WEB_SUBFOLDER=settings.WEB_SUBFOLDER)
        else:
            return Response(query_result, status=200, mimetype="application/rdf+json")
    # No query, display form
    else:
        query = request.args.get('query')
        return render_template('function_sparql.html',
                               query=query,
                               WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


@routes.route('/documentation', methods=['GET'])
def documentation():
    return render_template('documentation.html',
                           PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                           WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


@routes.route('/function/create_report', methods=['GET'])
def create_report():
    return render_template('function_create_report.html',
                           agents=functions.get_agents_dict(),
                           reportingsystems=functions.get_reportingsystems_dict(),
                           WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


@routes.route('/function/create_report_formparts', methods=['POST'])
def create_report_formparts(form_parts):
    return Response(functions.create_report_formparts(form_parts), status=200, mimetype='text/plain')


# TODO: this is a stub
@routes.route('/function/register_reporting_system', methods=['GET'])
def register_reporting_system():
    return render_template('function_register_reportingsystem.html',
                           WEB_SUBFOLDER = settings.WEB_SUBFOLDER)


@routes.route('/id/publickey')
def listPublicKey():
    usrs = User.list()
    return render_template("publickeys.html",
                           users=usrs,
                           WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


@routes.route('/id/publickey/<id>')
def getPublicKey(id=None):
    if id:
        user = User.find(id)
        return user['publickey']
    else:
        return ''





