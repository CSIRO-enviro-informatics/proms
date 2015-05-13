from flask import Blueprint, Response, request, redirect, render_template
routes = Blueprint('routes', __name__)
import functions
import functions_db
import urllib
import settings
import json


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
            #unencode the uri QSA
            uri = urllib.unquote(request.args.get('uri'))
            report = functions.get_report_dict(uri)
            return render_template('report.html',
                                   REPORT=report,
                                   PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI)
        #multiple Reports (register)
        else:
            reports = functions.get_reports_dict()
            return render_template('report.html',
                                   REPORTS=reports,
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
        entity = functions.get_entity_dict(uri)
        return render_template('entity.html',
                           ENTITY=entity)
    #multiple Entities (register)
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
        activity = functions.get_activity_dict(uri)
        return render_template('activity.html',
                               PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                               ACTIVITY=activity)
    #multiple Activities (register)
    else:
        activities = functions.get_activities_dict()
        return render_template('activity.html',
                               PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                               ACTIVITIES=activities)


@routes.route('/id/agent/', methods=['GET'])
def agents():
    #single Agent
    if request.args.get('uri'):
        #unencode the uri QSA
        uri = urllib.unquote(request.args.get('uri'))
        agent = functions.get_agent_dict(uri)
        return render_template('agent.html',
                               AGENT=agent)
    #multiple Agents (register)
    else:
        agents = functions.get_agents_dict()
        return render_template('agent.html',
                               PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                               AGENTS=agents)


@routes.route('/function/pingback', methods=['GET', 'POST'])
def pingback():
    if request.method == 'GET':
        return render_template('pingback.html')
    #process a pingback
    if request.method == 'POST':
        pass


@routes.route('/function/sparql/', methods=['GET', 'POST'])
def sparql():
    # Query submitted
    if request.method == 'POST':
        query = request.form['query']
        query_result = functions_db.db_query_secure(query)
        if query_result and 'results' in query_result:
            query_result = json.dumps(query_result['results']['bindings'])
        if 'form' in request.values and request.values['form'].lower() == 'true':
            return render_template('function_sparql.html',
                                   query=query,
                                   query_result=query_result)
        else:
            return Response(query_result, status=200, mimetype="application/rdf+json")
    # No query, display form
    else:
        query = request.args.get('query')
        return render_template('function_sparql.html',
                               query = query)


@routes.route('/documentation', methods=['GET'])
def documentation():
    return render_template('documentation.html', PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI)


@routes.route('/function/create_report', methods=['GET'])
def create_report():
    return render_template('function_create_report.html',
                           agents=functions.get_agents_dict(),
                           reportingsystems=functions.get_reportingsystems_dict())


@routes.route('/function/create_report_formparts', methods=['POST'])
def create_report_formparts(form_parts):
    return Response(functions.create_report_formparts(form_parts), status=200, mimetype='text/plain')


@routes.route('/function/register_reporting_system', methods=['GET'])
def register_reporting_system():
    return Response(functions.page_register_reporting_system(), status=200, mimetype='text/html')