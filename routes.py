from flask import Blueprint, Response, request
routes = Blueprint('routes', __name__)
import functions
import urllib


#
#   All the routes in the API
#
@routes.route('/')
def index():
    html = functions.get_proms_html_header()
    html += '''
    <h1>Provenance Management System</h1>
    <h4>This is the index page for PROMS, the Provenance Management Service</h4>
    <p style="font-style: italic;">Under development, November, 2014.</p>
    <p>This web service is not yet in operation and is acting only as a stub.</p>
    '''

    html += functions.get_proms_html_footer()
    return Response(html, status=200, mimetype='text/html')


@routes.route('/id/')
def ids():
    html = functions.get_proms_html_header()
    html += '''
    <h1>Provenance Management Service</h1>
    <h2>Endpoints</h2>
    <p style="font-style: italic;">Under development, October, 2014.</p>
    <p>The current registers (lists) of things that provenance reports sent to PROMS describe are:</p>
    <ul>
        <li><a href="/id/reportingsystem/">ReportingSystems</a></li>
        <li><a href="/id/report/">Reports</a></li>
        <li><a href="/id/entity/">Entities</a></li>
        <li><a href="/id/activity/">Activities</a></li>
        <li><a href="/id/agent/">Agents</a></li>
    </ul>
    <p>SPARQL endpoint for free-range queries:</p>
    <ul>
        <li><a href="/function/sparql">SPARQL Endpoint</a></li>
    </ul>
    '''

    html += functions.get_proms_html_footer()
    return Response(html, status=200, mimetype='text/html')


@routes.route('/id/reportingsystem/', methods=['GET', 'POST'])
def reportingsystem():
    if request.method == 'GET':
        #single Report
        if request.args.get('uri'):
            #unencode the uri QSA
            uri = urllib.unquote(request.args.get('uri'))
            html = functions.get_proms_html_header()
            html += '''
            <h1>Provenance Management Service</h1>
            <h2>A ReportingSystem</h2>
            <h3>URI: ''' + uri + '''</h3>
            <p style="font-style: italic;">Under development, November, 2014.</p>
            '''
            html += functions.get_reportingsystem_html(uri)
            html += functions.get_proms_html_footer()
            return Response(html, status=200, mimetype='text/html')
        #multiple Reports (register)
        else:
            html = functions.get_proms_html_header()
            html += '''
            <h1>Provenance Management Service</h1>
            <h2>ReportingSystems Register</h2>
            <p style="font-style: italic;">Under development, November, 2014.</p>
            '''
            reportingsystems = functions.get_reportingsystems()
            if reportingsystems[0]:
                html += functions.get_reportingsystems_html(reportingsystems[1])
            else:
                html += '<h4>There has been an error getting the ReportingSystems</h4>'
            html += functions.get_proms_html_footer()
            return Response(html, status=200, mimetype='text/html')
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


@routes.route('/id/report/', methods=['GET'])
@routes.route('/id/report/', methods=['GET', 'POST'])
def reports():
    if request.method == 'GET':
        #single Report
        if request.args.get('uri'):
            #unencode the uri QSA
            uri = urllib.unquote(request.args.get('uri'))
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
        #multiple Reports (register)
        else:
            html = functions.get_proms_html_header()
            html += '''
            <h1>Provenance Management Service</h1>
            <h2>Reports Register</h2>
            <p style="font-style: italic;">Under development, November, 2014.</p>
            '''
            reports = functions.get_reports()
            if reports[0]:
                html += functions.get_reports_html(reports[1])
            else:
                html += '<h4>There has been an error getting the Report</h4>'
            html += functions.get_proms_html_footer()
            return Response(html, status=200, mimetype='text/html')

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


@routes.route('/id/entity', methods=['GET'])
@routes.route('/id/entity/', methods=['GET'])
def entities():
    #single Entity
    if request.args.get('uri'):
        #unencode the uri QSA
        uri = urllib.unquote(request.args.get('uri'))
        html = functions.get_proms_html_header()
        html += '''
        <h1>Provenance Management Service</h1>
        <h2>An Entity</h2>
        <h3>URI: ''' + uri + '''</h3>
        <p style="font-style: italic;">Under development, November, 2014.</p>
        '''
        html += functions.get_entity_html(uri)
        html += functions.get_proms_html_footer()
        return Response(html, status=200, mimetype='text/html')
    #multiple Entities (register)
    else:
        html = functions.get_proms_html_header()
        html += '''
        <h1>Provenance Management Service</h1>
        <h2>Entities Register</h2>
        <p style="font-style: italic;">Under development, November, 2014.</p>
        '''

        e = functions.get_entities()
        if e[0]:
            html += functions.get_entities_html(e[1])
        else:
            html += '<h4>There has been an error getting the Entities</h4>'

        html += functions.get_proms_html_footer()
        return Response(html, status=200, mimetype='text/html')


@routes.route('/id/activity', methods=['GET'])
@routes.route('/id/activity/', methods=['GET'])
def activities():
    #single Report
    if request.args.get('uri'):
        #unencode the uri QSA
        uri = urllib.unquote(request.args.get('uri'))
        html = functions.get_proms_html_header()
        html += '''
        <h1>Provenance Management Service</h1>
        <h2>An Activity</h2>
        <h3>URI: ''' + uri + '''</h3>
        <p style="font-style: italic;">Under development, November, 2014.</p>
        '''
        html += functions.get_activity_html(uri)
        html += functions.get_proms_html_footer()
        return Response(html, status=200, mimetype='text/html')
    else:
        html = functions.get_proms_html_header()
        html += '''
        <h1>Provenance Management Service</h1>
        <h2>Activities Register</h2>
        <p style="font-style: italic;">Under development, November, 2014.</p>
        '''

        a = functions.get_activities()
        if a[0]:
            html += functions.get_activities_html(a[1])
        else:
            html += '<h4>There has been an error getting the Activities</h4>'

        html += functions.get_proms_html_footer()
        return Response(html, status=200, mimetype='text/html')


@routes.route('/id/agent/', methods=['GET'])
def agents():
    #single Agent
    if request.args.get('uri'):
        #unencode the uri QSA
        uri = urllib.unquote(request.args.get('uri'))
        html = functions.get_proms_html_header()
        html += '''
        <h1>Provenance Management Service</h1>
        <h2>An Agent</h2>
        <h3>URI: ''' + uri + '''</h3>
        <p style="font-style: italic;">Under development, November, 2014.</p>
        '''
        html += functions.get_agent_html(uri)
        html += functions.get_proms_html_footer()
        return Response(html, status=200, mimetype='text/html')
    #multiple Agents (register)
    else:
        html = functions.get_proms_html_header()
        html += '''
        <h1>Provenance Management Service</h1>
        <h2>Agents Register</h2>
        <p style="font-style: italic;">Under development, November, 2014.</p>
        '''

        a = functions.get_agents()
        if a[0]:
            html += functions.get_agents_html(a[1])
        else:
            html += '<h4>There has been an error getting the Agents</h4>'

        html += functions.get_proms_html_footer()
        return Response(html, status=200, mimetype='text/html')


@routes.route('/function/pingback', methods=['GET', 'POST'])
def pingback():
    if request.method == 'GET':
        html = functions.get_proms_html_header()
        html += '''
        <h1>Provenance Management Service</h1>
        <h2>Pingback Endpoint</h2>
        <p style="font-style: italic;">Under development, November, 2014.</p>
        <p>In future, other systems will be able to POST data to this endpoint to inform this PROMS server instance that a reference to one of the Entities listed here has been made in a provenance graph.</p>
        <p>This is in accordance with the idea of "Forward provenance" as per <a href="http://www.w3.org/TR/2013/WD-prov-aq-20130312/">PROV-AQ: Provenance Access and Query, W3C Working Draft 12 March 2013</a></p>
        '''

        html += functions.get_proms_html_footer()
        return Response(html, status=200, mimetype='text/html')

    #process a pingback
    if request.method == 'POST':
        pass


@routes.route('/function/sparql')
def sparql():
    return "SPARQL endpoint"


@routes.route('/documentation', methods=['GET'])
def documentation():
    return Response(functions.page_documentation(), status=200, mimetype='text/html')