from flask import Blueprint, Response, request
routes = Blueprint('routes', __name__)
import functions


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
    <p>The current registers (lists) of things that PROMS delivers for all its reports are:</p>
    <ul>
        <li><a href="/id/report">Reports</a></li>
        <li><a href="/id/entity">Entities</a></li>
        <li><a href="/id/activity">Activities</a></li>
    </ul>
    <p>SPARQL endpoint for free-range queries:</p>
    <ul>
        <li><a href="/function/sparql">SPARQL Endpoint</a></li>
    </ul>
    '''

    html += functions.get_proms_html_footer()
    return Response(html, status=200, mimetype='text/html')

@routes.route('/id/report/', methods=['GET'])
@routes.route('/id/report/', methods=['GET', 'POST'])
def reports():
    if request.method == 'GET':
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


@routes.route('/id/report/report', methods=['GET'])
def report():
    import urllib

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
    else:
        return Response('Requests to /id/report must specify a \'uri\' query string argument', status=400, mimetype='text/plain')


@routes.route('/id/entity', methods=['GET'])
@routes.route('/id/entity/', methods=['GET'])
def entities():
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


@routes.route('/id/entity/<string:entity_id>', methods=['GET'])
def entity(entity_id):
    return "An Entity, ID: " + entity_id


@routes.route('/id/activity', methods=['GET'])
@routes.route('/id/activity/', methods=['GET'])
def activities():
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
        html += '<h4>There has been an error getting the Entities</h4>'

    html += functions.get_proms_html_footer()
    return Response(html, status=200, mimetype='text/html')


@routes.route('/id/activity/<string:activity_id>', methods=['GET'])
def activity(activity_id):
    return "An activity, ID: " + activity_id


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
    html = functions.get_proms_html_header()
    html += '''
    <h1>Provenance Management Service</h1>
    <h2>Documentation for PROMS v3</h2>
    <p style="font-style: italic;">Under development, November, 2014.</p>
    <p>The function supported by PROMS v3 are:</p>
    <ul>
        <li>
            <strong>Create a new report</strong>
            <ul>
                <li>post a provenance <em>Report</em> to PROMS</li>
                <li>send a turtle document (RDF graph) to {PROMS_INSTANCE_URI}/id/report/</li>
            </ul>
        </li>
        <li>
            <strong>Create a pingback</strong> <em>(under development)</em>
            <ul>
                <li>let PROMS know you've referred to one of its <em>Entities</em> in a provenance graph elsewhere</li>
                <li>send a pingback JSON document to {PROMS_INSTANCE_URI}/function/pingback/</li>
            </ul>
        </li>
        <li>
            <strong>Browse <em>Reports</em> and their members</strong>
            <ul>
                <li>browse and filter <em>Reports</em> and their components <em>Entities</em> &amp; <em>Activities</em></li>
                <li><em>Reports</em> - <a href="/id/report/">{PROMS_INSTANCE_URI}/id/report/</a></li>
                <li><em>Entities</em> - <a href="/id/entity/">{PROMS_INSTANCE_URI}/id/entity/</a></li>
                <li><em>Activities</em> - <a href="/id/activity/">{PROMS_INSTANCE_URI}/id/activity/</a></li>
            </ul>
        </li>
        <li>
            <strong>Search the database</strong> <em>(under development)</em>
            <ul>
                <li>search the provenance data using PROM's SPARQL endpoint</li>
                <li><em>Activities</em> - <a href="/function/sparql">{PROMS_INSTANCE_URI}/function/sparql</a></li>
            </ul>
        </li>
    </ul>
    <h3>Documentation for PROMS and its related tools and concepts is maintained on the PROMS wiki:</h3>
    <ul>
        <li><a href="https://wiki.csiro.au/display/PROMS/">https://wiki.csiro.au/display/PROMS/</a></li>
    </ul>
    '''

    html += functions.get_proms_html_footer()
    return Response(html, status=200, mimetype='text/html')
