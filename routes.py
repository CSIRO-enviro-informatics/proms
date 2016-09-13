from flask import Blueprint, Response, request, redirect, render_template
from flask_httpauth import HTTPBasicAuth
import functions
import functions_db
import urllib
import settings
import json
from collections import Counter
import operator
from prom_db import PromDb
from user import User
auth = HTTPBasicAuth()
routes = Blueprint('routes', __name__)


#
#   All the routes in the API
#
@routes.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@routes.route('/')
def home():
    return render_template('index.html',
                           PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                           WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


@routes.route('/id/')
def ids():
    return render_template('id.html',
                           PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                           WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


@routes.route('/id/reportingsystem/', methods=['GET', 'POST'])
def reportingsystem():
    if request.method == 'GET':
        if request.args.get('uri'):
            rs = functions.get_reportingsystem_dict(request.args.get('uri'))
            return render_template('reportingsystem.html',
                                   REPORTINGSYSTEM=rs,
                                   WEB_SUBFOLDER=settings.WEB_SUBFOLDER)

        else:
            #if 'text/html' in request.headers.get('Accept'):
                rs = functions.get_reportingsystems_dict()
                return render_template('reportingsystem.html',
                                       REPORTINGSYSTEMS=rs,
                                       PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                                       WEB_SUBFOLDER=settings.WEB_SUBFOLDER)
            #else:
            #    if request.headers.get('rdf_object'):
            #        rdf_object = request.args.get('rdf_object')
            #        return Response(json.dumps(rdf_object), status_code=200, mimetype="application/rdf+json")

    # process a posted ReportingSystem
    if request.method == 'POST':
        # read the incoming report
        # only accept turtle POSTS
        if 'text/turtle' in request.headers['Content-Type']:
            put_result = functions.put_reportingsystem(request.data)
            if put_result[0]:
                reportingsystem_uri = put_result[1][0]
                link_header_content = '<' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/reportingsystem/?uri=' + reportingsystem_uri + '>; rel=http://promsns.org/def/proms#ReportingSystem'
                headers = {}
                headers['Content-Type'] = 'text/uri-list'
                headers['Link'] = link_header_content
                return Response(reportingsystem_uri, status=201, headers=headers)
            else:
                return Response('Insert failed for the following reasons:\n\n' + '\n'.join(put_result[1]), status=400, mimetype='text/plain')
        else:
            return Response('Only turtle documents allowed', status=400, mimetype='text/plain')


@routes.route('/id/report/', methods=['GET', 'POST'])
def reports():
    if request.method == 'GET':
        # single Report
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
                # TODO: v3.2
                '''
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
                '''
                return render_template('report.html',
                                       REPORT=report,
                                       PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                                       WEB_SUBFOLDER=settings.WEB_SUBFOLDER)
        # multiple Reports (register)
        else:
            if request.args.get('_format'):
                return Response('A specific report URI must be provided', status=400, mimetype='text/plain')
            else:
                reports = functions.get_reports_dict()
                # TODO: v3.2
                '''
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
                '''

                return render_template('report.html',
                                       REPORTS=reports,
                                       #SIGNED_REPORTS=signed_reports,
                                       PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                                       WEB_SUBFOLDER=settings.WEB_SUBFOLDER)

    # process a posted Report
    if request.method == 'POST':
        print 'POST'
        # read the incoming report, only accept turtle POSTS
        if 'text/turtle' in request.headers['Content-Type']:
            # check report conformance and insert if ok, reporting all errors
            put_result = functions.put_report(request.data)
            if put_result[0]:
                report_uri = put_result[1][0]
                link_header_content = '<' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/report/?uri=' + report_uri + '>; rel=http://promsns.org/def/proms#Report'
                headers = {}
                headers['Content-Type'] = 'text/uri-list'
                headers['Link'] = link_header_content
                return Response(report_uri, status=201, headers=headers)
            else:
                return Response('Report insert failed for the following reasons:\n\n' + '\n'.join(put_result[1]), status=400, mimetype='text/plain')
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
                                   ENTITY=entity,
                                   WEB_SUBFOLDER=settings.WEB_SUBFOLDER)
    #multiple Entities (register)
    else:
        if request.args.get('_format'):
            return Response('A specific Entity URI must be provided', status=400, mimetype='text/plain')
        else:
            entities = functions.get_entities_dict()
            return render_template('entity.html',
                                   PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                                   ENTITIES=entities,
                                   WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


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
    #single Person
    if request.args.get('uri'):
        #unencode the uri QSA
        uri = urllib.unquote(request.args.get('uri'))
        if request.args.get('_format'):
            if 'text/turtle' in request.args.get('_format'):
                response = functions.get_agent_rdf(uri)
                return Response(response, status=201, mimetype='text/turtle', headers={"Content-Disposition": "filename=Person.ttl"})
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


@routes.route('/function/pingback', methods=['POST'])
def pingback():
    """
    React to incoming pingback messages

    :return: 204 if PROV-AQ successful, 201 if PROMS successfull, else 400 or 500 + msg
    """
    import pingbacks.handle_incoming.hi_functions as hi

    # work out if it's a PROV-AQ message or a PROMS message
    if hi.is_provaq_msg(request):
        insert = hi.register_provaq_pingback(request)
        if insert[0]:
            return Response('', status=204)
        else:
            return Response('PROV-AQ pingback message not handled. ' + insert[1],
                            status=400,
                            mimetype='text/plain')
    elif hi.is_proms_msg(hi.register_provaq_pingback(request)):
        insert = hi.register_proms_pingback(request)
        if insert[0]:
            return Response('Created ' + insert[1] + ' triples.', status=201)
        else:
            return Response('PROMS pingback message not handled. ' + insert[1],
                            status=400,
                            mimetype='text/plain')
    else:
        # message not understood
        return Response('Pingback message not understood. Not recognised as PROV-AQ or PROMS msg.', status=400, mimetype='text/plain')

    pingback_result = functions.register_pingback(request.data)
    if pingback_result[0]:
        return Response('OK', status=200)
    else:
        return Response(pingback_result[1], status=400, mimetype='text/plain')


@routes.route('/function/sparql', methods=['GET', 'POST'])
def sparql():
    # Query submitted
    if request.method == 'POST':
        '''
        Pass on the SPARQL query to the underlying system PROMS is using (Fuseki etc.)
        '''
        if request.content_type == 'application/x-www-form-urlencoded':
            '''
            https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/#query-via-post-urlencoded

            2.1.2 query via POST with URL-encoded parameters

            Protocol clients may send protocol requests via the HTTP POST method by URL encoding the parameters. When
            using this method, clients must URL percent encode all parameters and include them as parameters within the
            request body via the application/x-www-form-urlencoded media type with the name given above. Parameters must
            be separated with the ampersand (&) character. Clients may include the parameters in any order. The content
            type header of the HTTP request must be set to application/x-www-form-urlencoded.
            '''
            if request.form.get('query') is None:
                return Response(
                    'Your POST request to PROMS\' SPARQL endpoint must contain a \'query\' parameter if form posting is used.',
                    status=400,
                    mimetype="text/plain")
            else:
                query = request.form.get('query')
        elif request.content_type == 'application/sparql-query':
            '''
            https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/#query-via-post-direct

            2.1.3 query via POST directly

            Protocol clients may send protocol requests via the HTTP POST method by including the query directly and
            unencoded as the HTTP request message body. When using this approach, clients must include the SPARQL query
            string, unencoded, and nothing else as the message body of the request. Clients must set the content type
            header of the HTTP request to application/sparql-query. Clients may include the optional default-graph-uri
            and named-graph-uri parameters as HTTP query string parameters in the request URI. Note that UTF-8 is the
            only valid charset here.
            '''
            query = request.data  # get the raw request
            if query is None:
                return Response(
                    'Your POST request to PROMS\' SPARQL endpoint must contain the query in plain text in the POST body if the Content-Type \'application/sparql-query\' is used.',
                    status=400,
                    mimetype="text/plain")

        # sorry, we only return JSON results. See the service description!
        query_result = functions_db.query(query)

        if query_result and 'results' in query_result:
            query_result = json.dumps(query_result['results']['bindings'])
        else:
            query_result = json.dumps(query_result)

        # resond to a form or with a raw result
        if 'form' in request.values and request.values['form'].lower() == 'true':
            return render_template('function_sparql.html',
                                   query=query,
                                   query_result=query_result,
                                   WEB_SUBFOLDER=settings.WEB_SUBFOLDER)
        else:
            return Response(json.dumps(query_result), status=200, mimetype="application/sparql-results+json")
    # No query, display form
    else:  # GET
        if request.args.get('query') is not None:
            # SPARQL GET request
            '''
            https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/#query-via-get

            2.1.1 query via GET

            Protocol clients may send protocol requests via the HTTP GET method. When using the GET method, clients must
            URL percent encode all parameters and include them as query parameter strings with the names given above.

            HTTP query string parameters must be separated with the ampersand (&) character. Clients may include the
            query string parameters in any order.

            The HTTP request MUST NOT include a message body.
            '''
            # following check invalid due to higher order if/else
            # if request.args.get('query') is None:
            #     return Response(
            #         'Your GET request to PROMS\' SPARQL endpoint must contain a \'query\' query string argument.',
            #         status=400,
            #         mimetype="text/plain")
            query = request.args.get('query')
            print query
            query_result = functions_db.query(query)
            print query_result
            return Response(json.dumps(query_result), status=200, mimetype="application/sparql-results+json")
        else:
            # SPARQL Service Description
            '''
            https://www.w3.org/TR/sparql11-service-description/#accessing

            SPARQL services made available via the SPARQL Protocol should return a service description document at the
            service endpoint when dereferenced using the HTTP GET operation without any query parameter strings provided.
            This service description must be made available in an RDF serialization, may be embedded in (X)HTML by way of
            RDFa, and should use content negotiation if available in other RDF representations.
            '''
            best = request.accept_mimetypes.best_match([
                'text/turtle',
                'text/n3',
                'application/rdf+json',
                'application/rdf+xml',
                'text/html'
            ])
            if best != 'text/html':
                if best == "text/n3":
                    return Response(functions.get_sparql_service_description('n3'),
                                    status=200,
                                    mimetype='text/n3')
                elif best == "application/json":
                    return Response(functions.get_sparql_service_description('json-ld'),
                                    status=200,
                                    mimetype='application/json')
                elif best == "application/rdf+xml":
                    return Response(functions.get_sparql_service_description('xml'),
                                    status=200,
                                    mimetype='application/rdf+xml')
                else:  # turtle
                    return Response(functions.get_sparql_service_description('turtle'),
                                    status=200,
                                    mimetype='text/turtle')
            else:  #text/html
                # show the SPARQL query form
                query = request.args.get('query')
                return render_template('function_sparql.html',
                                       query=query,
                                       WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


@routes.route('/about', methods=['GET'])
def about():
    import subprocess
    version = subprocess.check_output(["git", "describe"]).rstrip().replace('v', '').split('-')[0]

    return render_template('about.html',
                           PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                           WEB_SUBFOLDER=settings.WEB_SUBFOLDER,
                           VERSION=version)


@routes.route('/function/create_report', methods=['GET'])
def create_report():
    reportingsystems = functions.get_reportingsystems_dict()
    import pprint
    pprint.pprint("test " + str(reportingsystems))
    return render_template('function_create_report.html',
                           agents=functions.get_agents_dict(),
                           entities=functions.get_entities_dict(),
                           reportingsystems=reportingsystems,
                           WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


@routes.route('/function/create_report_formparts', methods=['POST'])
def create_report_formparts(form_parts):
    return Response(functions.create_report_formparts(form_parts), status=200, mimetype='text/plain')


# TODO: this is a stub
@routes.route('/function/register_reportingsystem', methods=['GET'])
def register_reporting_system():
    agents = functions.get_agents_dict()
    return render_template('function_register_reportingsystem.html',
                           agents=agents,
                           WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


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





