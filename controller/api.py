import json
from flask import Blueprint, Response, request, render_template, url_for
from requests.exceptions import ConnectionError
import controller.api_functions
from _database import queries
from modules.ldapi import LDAPI
import controller.api_functions as api_functions
import controller.class_reportingsystems as class_reportingsystems
import controller.class_agents as class_agents
import controller.class_reports as class_reports
import controller.class_pingbacks as class_pingbacks
import _config as conf

api = Blueprint('api', __name__)


@api.route('/function/lodge-agent', methods=['POST'])
def lodge_agent():
    """Insert an Agent into the provenance _database"""
    # only accept RDF documents
    acceptable_mimes = LDAPI.get_rdf_mimetypes_list()
    ct = request.content_type
    if ct not in acceptable_mimes:
        return api_functions.client_error_response(
            'The Agent posted is not encoded with a valid RDF Content-Type. Must be one of: ' +
            ', '.join(acceptable_mimes) + '.')

    # validate Agent
    sr = class_agents.IncomingAgent(request.data, request.content_type)
    if not sr.valid():
        return api_functions.client_error_response(
            'The Agent posted is not valid for the following reasons: ' +
            ', '.join(sr.error_messages) + '.')

    # get the Agent's URI
    sr.determine_uri()

    # store the Agent
    if not sr.stored():
        return api_functions.server_error_response(
            'The Agent posted is valid but cannot be stored for the following reasons: ' +
            ', '.join(sr.error_messages) + '.')

    # reply to sender
    return Response(
        sr.uri,
        status=201,
        mimetype='text/plain')


@api.route('/function/create-agent')
def create_agent():
    """Create an Agent for inserting into the provenance _database using an HTML web form"""
    try:
        agents = controller.api_functions.get_agents()
    except ConnectionError:
        return render_template('error_db_connection.html'), 500
    return render_template(
        'function_create_agent.html',
        agents=agents
    )


@api.route('/function/lodge-reportingsystem', methods=['POST'])
def lodge_reportingsystem():
    """Insert a ReportingSystem into the provenance _database"""
    # only accept RDF documents
    acceptable_mimes = LDAPI.get_rdf_mimetypes_list()
    ct = request.content_type
    if ct not in acceptable_mimes:
        return api_functions.client_error_response(
            'The ReportingSystem posted is not encoded with a valid RDF Content-Type. Must be one of: ' +
            ', '.join(acceptable_mimes) + '.')

    # validate ReportingSystem
    rs = class_reportingsystems.IncomingReportingSystem(request)
    if not rs.valid():
        return api_functions.client_error_response(
            'The ReportingSystem posted is not valid for the following reasons: ' +
            ', '.join(rs.error_messages) + '.')

    # get the ReportingSystem's URI
    rs.determine_uri()

    rs.generate_named_graph_metadata()

    # store the ReportingSystem
    if not rs.stored():
        return api_functions.server_error_response(
            'ReportingSystem posted is valid but cannot be stored for the following reasons: ' +
            ', '.join(rs.error_messages) + '.')

    # reply to sender
    return Response(
        rs.uri,
        status=201,
        mimetype='text/plain')


@api.route('/function/create-reportingsystem')
def create_reportingsystem():
    """Create a ReportingSystem for inserting into the provenance _database using an HTML web form"""
    try:
        agents = controller.api_functions.get_agents()
    except ConnectionError:
        return render_template('error_db_connection.html'), 500
    return render_template(
        'function_create_reportingsystem.html',
        agents=agents
    )


@api.route('/function/lodge-report', methods=['POST'])
def lodge_report():
    """Insert a Report into the provenance database

    This function should be edited if any custom actions are to be undertaken by PROMS on reciept of a Report, such as
    Ppingbacks
    """
    # only accept RDF documents
    acceptable_mimes = LDAPI.get_rdf_mimetypes_list()
    ct = request.content_type
    if ct not in acceptable_mimes:
        return api_functions.client_error_response(
            'The Report posted is not encoded with a valid RDF Content-Type. Must be one of: ' +
            ', '.join(acceptable_mimes) + '.')

    # validate Report, using the controller validator class, IncomingReport
    r = class_reports.IncomingReport(request)
    if not r.valid():
        return api_functions.client_error_response(
            'The Report posted is not valid for the following reasons: ' + ', '.join(r.error_messages) + '.')

    # TODO: implement Named Graph annotation metadata
    ''' UNUSED yet
    # this code is incomplete. It is to generate Named Graph metadata so Reports flowing to PROMS can each be stored in 
    annotated Named Graphs
    # get the Report's URI
    r.determine_uri()

    r.generate_named_graph_metadata()
    '''

    # store the Report
    if not r.stored():
        return api_functions.server_error_response(
            'Report posted is valid but cannot be stored for the following reasons: ' +
            ', '.join(r.error_messages) + '.')

    # Custom Actions
    # Only try to any custom actions, e.g. Pingbacks, if the module is turned on
    if conf.MODULES.get('pingbacks').get('valid'):
        # kick off any Pingbacks for this Report, as per chosen Pingbacks strategies
        # TODO: split Pingbacks process off into another thread
        from modules.pingbacks.engine import Engine
        e = Engine(r.graph, r.uri, url_for('modelx.instance'), url_for('.sparql'))

    # reply to sender
    return r.uri, 201


@api.route('/function/create-report')
def create_report():
    """Create a Report for inserting into the provenance _database using an HTML web form"""
    try:
        reportingsystems = controller.api_functions.get_reportingsystems()
        agents = controller.api_functions.get_agents()
        entities = controller.api_functions.get_entities()
    except ConnectionError:
        return render_template('error_db_connection.html'), 500

    return render_template(
        'function_create_report.html',
        agents=agents,
        entities=entities,
        reportingsystems=reportingsystems
    )


@api.route('/function/lodge-pingback', methods=['POST'])
def lodge_pingback():
    """Insert an Pingback into the provenance _database' pingbacks data named graph"""
    # only valid Pingback Cotent-Types
    acceptable_mimes = class_pingbacks.IncomingPingback.acceptable_mimes
    ct = request.content_type
    if ct not in acceptable_mimes:
        return api_functions.client_error_response(
            'The Pingback posted is not encoded with a valid Content-Type. Must be one of: ' +
            ', '.join(acceptable_mimes) + '.')

    # validate Pingback
    p = class_pingbacks.IncomingPingback(request)
    if not p.valid():
        return api_functions.client_error_response(
            'The Pingback posted is not valid for the following reasons: ' + ', '
            .join(p.error_messages) + '.')

    # get the Pingback's URI
    p.determine_uri()

    # convert the Pingback to RDF -- no need to test this step as successful validation, needed to get this far, ensures
    # it can be converted
    # this function also generated Named Graph metadata
    p.convert_pingback_to_rdf()

    p.generate_named_graph_metadata()

    # store the Pingback's RDF
    if not p.stored():
        return api_functions.server_error_response(
            'Report posted is valid but cannot be stored for the following reasons: , '
            .join(p.error_messages) + '.')

    # reply to sender
    return '', 204  # PROV-AQ says to return an empty 204 response


@api.route('/function/sparql', methods=['GET', 'POST'])
def sparql():
    # Query submitted
    if request.method == 'POST':
        '''
        Pass on the SPARQL query to the underlying system PROMS is using (Fuseki etc.)
        '''
        query = None
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
                return api_functions.client_error_response(
                    'Your POST request to PROMS\' SPARQL endpoint must contain a \'query\' parameter if form '
                    'posting is used.')
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
                return api_functions.client_error_response(
                    'Your POST request to PROMS\' SPARQL endpoint must contain the query in plain text in the '
                    'POST body if the Content-Type \'application/sparql-query\' is used.')

        # sorry, we only return JSON results. See the service description!
        try:
            query_result = queries.query(query)
        except ValueError as e:
            return render_template(
                'function_sparql.html',
                query=query,
                query_result='No results: ' + e.message
            ), 400
        except ConnectionError:
            return render_template('error_db_connection.html'), 500

        if query_result and 'results' in query_result:
            query_result = json.dumps(query_result['results']['bindings'])
        else:
            query_result = json.dumps(query_result)

        # resond to a form or with a raw result
        if 'form' in request.values and request.values['form'].lower() == 'true':
            return render_template(
                'function_sparql.html',
                query=query,
                query_result=query_result
            )
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
            query_result = queries.query(query)
            return Response(json.dumps(query_result), status=200, mimetype="application/sparql-results+json")
        else:
            # SPARQL Service Description
            '''
            https://www.w3.org/TR/sparql11-service-description/#accessing

            SPARQL services made available via the SPARQL Protocol should return a service description document at the
            service endpoint when dereferenced using the HTTP GET operation without any query parameter strings
            provided. This service description must be made available in an RDF serialization, may be embedded in
            (X)HTML by way of RDFa, and should use content negotiation if available in other RDF representations.
            '''

            acceptable_mimes = [x[0] for x in LDAPI.MIMETYPES_PARSERS] + ['text/html']
            best = request.accept_mimetypes.best_match(acceptable_mimes)
            if best == 'text/html':
                # show the SPARQL query form
                query = request.args.get('query')
                return render_template(
                    'function_sparql.html',
                    query=query
                )
            elif best is not None:
                return Response(
                    api_functions.get_sparql_service_description(
                        [item for item in LDAPI.MIMETYPES_PARSERS if item[0] == best]
                    ),
                    status=200,
                    mimetype=best)
            else:
                return api_functions.client_error_response(
                    'Accept header must be one of ' + ', '.join(acceptable_mimes) + '.')
