from requests.exceptions import ConnectionError
import json
from flask import Blueprint, Response, request, render_template
import functions
import functions_reports
import functions_reportingsystems
import functions_agents
import functions_entities
import functions_sparqldb
import api_functions
import settings
from ldapi import LDAPI
api = Blueprint('api', __name__)



@api.route('/function/new_report', methods=['POST'])
def new_report():
    pass


@api.route('/function/pingback', methods=['POST'])
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


# TODO: tidy up with templates, inc. error_db_connection
@api.route('/function/sparql', methods=['GET', 'POST'])
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
        query_result = functions_sparqldb.query(query)

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
            query_result = functions_sparqldb.query(query)
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

            acceptable_mimes = [x[0] for x in LDAPI.MIMETYPES_PARSERS] + ['text/html']
            best = request.accept_mimetypes.best_match(acceptable_mimes)
            if best == 'text/html':
                # show the SPARQL query form
                query = request.args.get('query')
                return render_template(
                    'function_sparql.html',
                    query=query,
                    web_subfolder=settings.WEB_SUBFOLDER)
            elif best is not None:
                return Response(
                    api_functions.get_sparql_service_description([item for item in LDAPI.MIMETYPES_PARSERS if item[0] == best]),
                    status=200,
                    mimetype=best)
            else:
                return 'Accpet mimetype must be one of ' + ', '.join(acceptable_mimes) + '.', 404


@api.route('/function/create_report')
def create_report():
    try:
        reportingsystems = functions_reportingsystems.get_reportingsystems_dict()
        agents = functions_agents.get_agents_dict()
        entities = functions_entities.get_entities_dict()
    except ConnectionError:
        return render_template('error_db_connection.html'), 500

    return render_template(
        'function_create_report.html',
        agents=agents,
        entities=entities,
        reportingsystems=reportingsystems,
        web_subfolder=settings.WEB_SUBFOLDER
    )


@api.route('/function/create_report_formparts', methods=['POST'])
def create_report_formparts(form_parts):
    return Response(functions_reports.create_report_formparts(form_parts), status=200, mimetype='text/plain')


# TODO: this is a stub
@api.route('/function/register_reportingsystem')
def register_reporting_system():
    try:
        agents = functions_agents.get_agents_dict()
    except ConnectionError:
        return render_template('error_db_connection.html'), 500
    return render_template(
        'function_register_reportingsystem.html',
        agents=agents,
        web_subfolder=settings.WEB_SUBFOLDER
    )
