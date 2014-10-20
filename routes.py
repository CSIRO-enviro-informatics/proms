from flask import Blueprint, Response
routes = Blueprint('routes', __name__)
import functions


#
#   All the routes in the API
#
@routes.route('/')
def index():
    html = functions.get_proms_html_header()
    html += '''
    <h1>Provenance Management Service</h1>
    <h4>This is the index page for PROMS, the Provenance Management Service</h4>
    <p style="font-style: italic;">Under development, October, 2014.</p>
    <p>This web service is not yet in operation and is acting only as a stub.</p>
    '''

    html += functions.get_proms_html_footer()
    return Response(html, status=200, mimetype='text/html')


@routes.route('/endpoints')
def endpoints():
    html = functions.get_proms_html_header()
    html += '''
    <h1>Provenance Management Service</h1>
    <h2>Endpoints</h2>
    <p style="font-style: italic;">Under development, October, 2014.</p>
    <p>The current registers (lists) of things that PROMS delivers for all its reports are:</p>
    <ul>
        <li><a href="/report">Reports</a></li>
        <li><a href="/entity">Entities</a></li>
        <li><a href="/activity">Activities</a></li>
    </ul>
    '''

    html += functions.get_proms_html_footer()
    return Response(html, status=200, mimetype='text/html')


@routes.route('/report')
def reports():
    return "Reports"


@routes.route('/report/<string:report_id>')
def report(report_id):
    return "A report, ID: " + report_id


@routes.route('/entity')
def entities():
    return "Entities"


@routes.route('/entity/<string:entity_id>')
def entity(entity_id):
    return "An Entity, ID: " + entity_id


@routes.route('/activity')
def activities():
    return "Activities"


@routes.route('/activity/<string:activity_id>')
def activity(activity_id):
    return "An activity, ID: " + activity_id


@routes.route('/documentation')
def documentation():
    html = functions.get_proms_html_header()
    html += '''
    <h1>Provenance Management Service</h1>
    <h2>Documentation for PROMS v3</h2>
    <p style="font-style: italic;">Under development, October, 2014.</p>
    <h3>Documentation for PROMS and its related tools and concepts is maintained on the PROMS wiki:</h3>
    <ul>
        <li><a href="https://wiki.csiro.au/display/PROMS/">https://wiki.csiro.au/display/PROMS/</a></li>
    </ul>
    '''

    html += functions.get_proms_html_footer()
    return Response(html, status=200, mimetype='text/html')


@routes.route('/sparql')
def sparql():
    return "SPARQL endpoint"
