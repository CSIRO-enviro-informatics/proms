import urllib
from flask import Blueprint, Response, request, redirect, render_template
from flask_httpauth import HTTPBasicAuth
import settings
# from secure.user import User
auth = HTTPBasicAuth()
functions = Blueprint('functions', __name__)


@functions.route('/class/')
def classes():
    return render_template('classes.html',
                           PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                           WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


@functions.route('/class/reportingsystem/', methods=['GET', 'POST'])
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


@functions.route('/class/report/', methods=['GET', 'POST'])
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


@functions.route('/class/report/<regex(".{36}"):report_id><regex("(\..{3,4})?"):extension>')
def report_id(report_id, extension):
    # we're only handling turtl & HTML docs for now
    # we forward on the accept header/_format directive or extension as an extension

    # check requested format
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


@functions.route('/doc/report/<regex(".{36}"):report_id><regex("(\..{3,4})?"):extension>')
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
        # this code is the same as for /class/report/?url=X
        # TODO: de-duplicate this code
        uri = request.url
        #get back the original URI
        uri = uri.replace('/doc/', '/class/')
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


@functions.route('/class/entity')
@functions.route('/class/entity/')
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


@functions.route('/class/activity')
@functions.route('/class/activity/')
def activities():
    # single Activity
    if request.args.get('uri'):
        # unencode the uri QSA
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
    # multiple Activities (register)
    else:
        if request.args.get('_format'):
            return Response('A specific Entity URI must be provided', status=400, mimetype='text/plain')
        else:
            activities = functions.get_activities_dict()
            return render_template('activity.html',
                                   PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                                   ACTIVITIES=activities,
                                   WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


@functions.route('/class/agent/')
def agents():
    # single Person
    if request.args.get('uri'):
        # unencode the uri QSA
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
    # multiple Agents (register)
    else:
        if request.args.get('_format'):
            return Response('A specific Entity URI must be provided', status=400, mimetype='text/plain')
        else:
            agents = functions.get_agents_dict()
            return render_template('agent.html',
                                   PROMS_INSTANCE_NAMESPACE_URI=settings.PROMS_INSTANCE_NAMESPACE_URI,
                                   AGENTS=agents,
                                   WEB_SUBFOLDER=settings.WEB_SUBFOLDER)


#   Secure prov endpoints
#
# @functions.route('/class/publickey')
# def listPublicKey():
#     usrs = User.list()
#     return render_template("publickeys.html",
#                            users=usrs,
#                            WEB_SUBFOLDER=settings.WEB_SUBFOLDER)
#
#
# @functions.route('/class/publickey/<id>')
# def getPublicKey(id=None):
#     if id:
#         user = User.find(id)
#         return user['publickey']
#     else:
#         return ''





