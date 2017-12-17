import _config as conf
from rdflib import URIRef
import modules.pingbacks.engine as engine


# Strategy 1: Given Pingback
def try_strategy_1(g, excluded_entities=[]):
    # Get the URIs of the Entities for pingbacks
    entities = engine.get_candidates(g)

    # remove those Entities specifically excluded (as a result of other strategies)
    for entity in excluded_entities:
        entities.remove(entity)

    # For each Entity, look for a prov:pingback property
    entities_with_pingback_uris = []
    for entity in entities:
        q = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE {
                ?s ?p ?o .
                <''' + entity + '''> prov:pingback ?o .
            }
        '''
        for row in g.query(q):
            entities_with_pingback_uris.append({
                'entity': str(row['s']),
                'pingback_endpoint': str(row['o'])}
            )

    successful_pingbacks = []
    for entity in entities_with_pingback_uris:
        pingback_uri = entity['pingback_endpoint']
        entity_uri = [entity['entity']]
        result = engine.send_pingback(pingback_uri, entity_uri, further_links=[])
        if result[0]:
            successful_pingbacks.append(entity_uri)

    # return the list of entities for which pingbacks were attempted and entities for which pingbacks were successful
    return {
        'pingback_attempt': entities_with_pingback_uris,
        'pingback_successful': successful_pingbacks
    }


# Strategy 2: Given Provenance
def try_strategy_2(g, excluded_entities=[]):
    # Get the URIs of the Entities for pingbacks
    entities = engine.get_candidates(g)

    # remove those Entities specifically excluded (as a result of other strategies)
    for entity in excluded_entities:
        entities.remove(entity)

    # Get any Entities with a prov:has_provenance, prov:has_query_service or dct:provenance property
    # If one is found, stage for the sending of provenance information bundles
    entities_with_provenance_locations = []
    entities_with_provenance_query_services = []
    for entity in entities:
        q = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX dc11: <http://purl.org/dc/elements/1.1/>
            SELECT *
            WHERE {
                ?s ?p ?o .
                {<''' + entity + '''> prov:has_provenance ?o .}
                UNION
                {<''' + entity + '''> dc11:provenance ?o .}
                UNION
                {<''' + entity + '''> prov:has_query_service ?o .}
            }
        '''
        for row in g.query(q):
            if str(row['p']) in ['http://www.w3.org/ns/prov#has_provenance', 'http://purl.org/dc/elements/1.1/provenance']:
                entities_with_provenance_locations.append({
                    'entity': str(row['s']),
                    'provenance_location': str(row['o'])
                })
            elif str(row['p']) == 'http://www.w3.org/ns/prov#has_query_service':
                entities_with_provenance_query_services.append({
                    'entity': str(row['s']),
                    'provenance_service': str(row['o'])
                })

    # return the list of entities for which pingbacks were attempted and entities for which pingbacks were successful
    return {
        'pingback_attempt': [],
        'pingback_successful': []
    }


# Strategy 3: Known Provenance Stores
def try_strategy_3(g, excluded_entities=[]):
    # Get the URIs of the Entities for pingbacks
    entities = engine.get_candidates(g)

    # remove those Entities specifically excluded (as a result of other strategies)
    for entity in excluded_entities:
        entities.remove(entity)

    successful_pingbacks = []
    for entity in entities:
        # make all the PROV-AQ links for each entity
        further_links = [
            {
                'resource': entity,
                'rel': 'has_query_service',
                'anchor': conf.PROMS_INSTANCE_NAMESPACE_URI + '/function/sparql'
            },
            {
                'resource': entity,
                'rel': 'has_provenance',
                'anchor': conf.ENTITY_BASE_URI + '/?uri=' + entity
            }
        ]
        for known_store_pingback_endpoints in conf.KNOWN_PROVENANCE_STORE_PINGBACK_ENDPOINTS:
            if known_store_pingback_endpoints != '':
                #result = send_provaq_pingback(known_store_pingback_endpoints, None, further_links)
                proms_pingback_msg = generate_proms_msg_from_report(g, entities, known_store_pingback_endpoints)
                result1 = send_proms_pingback(known_store_pingback_endpoints, proms_pingback_msg)
                #if result[0]:
                #    successful_pingbacks.append(entity)

    # return the list of entities for which pingbacks were attempted and entities for which pingbacks were successful
    return {
        'pingback_attempt': entities,
        'pingback_successful': successful_pingbacks
    }


# Strategy 4: Pingback Lookup
def try_strategy_4(g, excluded_entities=[]):
    # Get the URIs of the Entities for pingbacks
    entities = engine.get_candidates(g)

    # remove those Entities specifically excluded (as a result of other strategies)
    for entity in excluded_entities:
        entities.remove(entity)

    # For each Entity, follow it's URI to look for a prov:pingback property
    entities_with_pingback_uris = []
    for entity in entities:
        """
        # look for an RDF description of the Entity
        rdf = engine.get_entity_rdf(entity)
        if rdf[0]:
            print(entity)
            print(rdf[1])
        else:
            print entity
            print 'failed to get RDF'
        """
        pingback_endpoints = get_pingback_endpoints_via_lookup(g, entity)
        if len(pingback_endpoints) > 0:
            entities_with_pingback_uris.append({
                'entity': entity,
                'pingback_endpoints': pingback_endpoints
            })

    successful_pingbacks = []
    for entity in entities_with_pingback_uris:
        entity_uri = [entity['entity']]
        pingback_uris = entity['pingback_endpoints']
        for pingback_uri in pingback_uris:
            result = engine.send_pingback(pingback_uri, entity_uri, further_links=[])
            if result[0]:
                successful_pingbacks.append(entity_uri)

    # return the list of entities for which pingbacks were attempted and entities for which pingbacks were successful
    return {
        'pingback_attempt': entities_with_pingback_uris,
        'pingback_successful': successful_pingbacks
    }


# Endpoint Lookup Discovery
def try_strategy_5(g, excluded_entities=[]):
    # Get the URIs of the Entities for pingbacks
    entities = engine.get_candidates(g)

    # remove those Entities specifically excluded (as a result of other strategies)
    for entity in excluded_entities:
        entities.remove(entity)

    entities_with_pingback_uris = []
    for entity in entities:
        query_service_endpoints = get_has_query_service_endpoints_via_lookup(g, entity)
        if len(query_service_endpoints) > 0:
            entities_with_pingback_uris.append({
                'entity': entity,
                'pingback_endpoints': query_service_endpoints
            })

    successful_pingbacks = []
    for entity in entities_with_pingback_uris:
        pingback_uris = entity['pingback_endpoints']
        entity_uri = [entity['entity']]
        for pingback_uri in pingback_uris:
            result = engine.send_pingback(pingback_uri, entity_uri, further_links=[])
            if result[0]:
                if entity_uri not in successful_pingbacks:
                    successful_pingbacks.append(entity_uri)

    # return the list of entities for which pingbacks were attempted and entities for which pingbacks were successful
    return {
        'pingback_attempt': entities,
        'pingback_successful': successful_pingbacks
    }


# Strategy 6: Data Provider Node Given
# not described in paper yet
def try_strategy_6(g, excluded_entities=[]):
    # Get the URIs of the Entities for pingbacks
    entities = engine.get_candidates(g)

    # remove those Entities specifically excluded (as a result of other strategies)
    for entity in excluded_entities:
        entities.remove(entity)


# Strategy 6: Data Provider Node Lookup
# not described in paper yet
def try_strategy_7(g, excluded_entities=[]):
    # Get the URIs of the Entities for pingbacks
    entities = engine.get_candidates(g)

    # remove those Entities specifically excluded (as a result of other strategies)
    for entity in excluded_entities:
        entities.remove(entity)


# Strategy 1: Given Pingback
def get_pingback_endpoints_via_given(g, entity_uri):
    pingback_endpoints = []
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?pb
        WHERE {
            <''' + entity_uri + '''> a prov:Entity .
            <''' + entity_uri + '''> prov:pingback ?pb .
        }
    '''
    for row in g.query(q):
        pingback_endpoints.append(str(row['pb']))
    return pingback_endpoints


# Strategy 2: Given Provenance
def get_has_query_service_endpoints_via_given(g, entity_uri):
    provenance_endpoints = []
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?ps
        WHERE {
            <''' + entity_uri + '''> a prov:Entity ;
                prov:has_query_service ?ps .
        }
    '''
    for row in g.query(q):
        provenance_endpoints.append(str(row['ps']))
    return provenance_endpoints


# Strategies 4 & 5
def is_dereferencable(entity_uri):
    import requests
    from requests import exceptions

    headers = {'Accept': 'text/turtle;q=1,application/ld+json;q=0.75,application/rdf+xml;q=0.5'}
    try:
        r = requests.get(entity_uri, headers=headers, allow_redirects=True)
        if r.status_code == 200:
            return [True, r.text, r.headers]
        else:
            return [False, 'Could not dereference URI']
    except exceptions.RequestException as e:
        return [False, 'Could not dereference URI']


# Strategies 4 & 5
def has_valid_rdf_meatadata(rdf_metadata, content_type_header):
    # test header. Must find one of three known RDF serialisations
    if 'text/turtle' in content_type_header:
        format = 'turtle'
    elif 'application/ld+json' in content_type_header:
        format = 'json-ld'
    elif 'application/rdf+xml' in content_type_header:
        format = 'xml'
    else:
        return [False, 'no RDF format given in header']

    if format is not None:
        from rdflib import Graph
        try:
            g = Graph().parse(data=rdf_metadata, format=format)
            return [True, g]
        except Exception as e:
            return [False, 'RDF format ' + format + ' indicated in header but unable to parse RDF data to graph. Error: ' + e.message]


# Strategy 4: Pingback Lookup
def get_pingback_endpoints_via_lookup(g, entity_uri):
    pingback_endpoints = []

    # find prov:pingback properties defined for this Entity
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?pb
        WHERE {
            <''' + entity_uri + '''> a prov:Entity ;
                prov:pingback ?pb .
        }
    '''

    for row in g.query(q):
        pingback_endpoints.append(str(row['pb']))

    # find prov:pingback properties defined on a dcat:CatalogRecord for this dcat:Dataset
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?pb
        WHERE {
            {
                <''' + entity_uri + '''> a dcat:Dataset ;
                    foaf:isPrimaryTopicOf ?cr .
                ?cr prov:pingback ?pb .
            }
            UNION
            {
                ?cr a dcat:CatalogRecord ;
                    foaf:primaryTopic <''' + entity_uri + '''> ;
                    prov:pingback ?pb .
            }
        }
    '''

    for row in g.query(q):
        pingback_endpoints.append(str(row['pb']))

    # find a dpn:Service class object, of type dpns:ProvenancePingbackService, that has the property dpn:hostsDataset indicating the Entity URI.
    # TODO: build a test dataset for this combo
    q = '''
        PREFIX dpn: <http://purl.org/dpn#>
        PREFIX dpns: <http://purl.org/dpn/services#>
        SELECT ?pb
        WHERE {
            ?s a dpns:ProvenancePingbackService ;
                dpns:hostsDataset <''' + entity_uri + '''> ;
                dpn:endpoint ?pb .
        }
    '''

    for row in g.query(q):
        pingback_endpoints.append(str(row['pb']))

    return pingback_endpoints


# Strategy 5: Provenance Lookup
def get_has_query_service_endpoints_via_lookup(g, entity_uri):
    has_query_service_endpoints = []

    # find prov:has_query_service properties defined for this Entity
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?pb
        WHERE {
            <''' + entity_uri + '''> a prov:Entity ;
                prov:has_query_service ?pb .
        }
    '''

    for row in g.query(q):
        has_query_service_endpoints.append(str(row['pb']))

    # find prov:has_query_service properties defined on a dcat:CatalogRecord for this dcat:Dataset
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?pb
        WHERE {
            {
                <''' + entity_uri + '''> a dcat:Dataset ;
                    foaf:isPrimaryTopicOf ?cr .
                ?cr prov:has_query_service ?pb .
            }
            UNION
            {
                ?cr a dcat:CatalogRecord ;
                    foaf:primaryTopic <''' + entity_uri + '''> ;
                    prov:has_query_service ?pb .
            }
        }
    '''

    for row in g.query(q):
        has_query_service_endpoints.append(str(row['pb']))

    # find a dpn:Service class object, of type dpns:ProvenanceService, that has the property dpn:hostsDataset indicating the Entity URI.
    # TODO: build a test dataset for this combo
    q = '''
        PREFIX dpn: <http://purl.org/dpn#>
        PREFIX dpns: <http://purl.org/dpn/services#>
        SELECT ?pb
        WHERE {
            ?s a dpns:ProvenanceService ;
                dpns:hostsDataset <''' + entity_uri + '''> ;
                dpn:endpoint ?pb .
        }
    '''

    for row in g.query(q):
        has_query_service_endpoints.append(str(row['pb']))

    return has_query_service_endpoints


def is_a_uri(uri_candidate):
    """
    Validates a string as a URI

    :param uri_candidate: string
    :return: True or False
    """
    import re
    # https://gist.github.com/dperini/729294
    URL_REGEX = re.compile(
        u"^"
        # protocol identifier
        u"(?:(?:https?|ftp)://)"
        # user:pass authentication
        u"(?:\S+(?::\S*)?@)?"
        u"(?:"
        # IP address exclusion
        # private & local networks
        u"(?!(?:10|127)(?:\.\d{1,3}){3})"
        u"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
        u"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
        # IP address dotted notation octets
        # excludes loopback network 0.0.0.0
        # excludes reserved space >= 224.0.0.0
        # excludes network & broadcast addresses
        # (first & last IP address of each class)
        u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
        u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
        u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
        u"|"
        # host name
        u"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
        # domain name
        u"(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
        # TLD identifier
        u"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
        u")"
        # port number
        u"(?::\d{2,5})?"
        # resource path
        u"(?:/\S*)?"
        u"$"
        , re.UNICODE
    )
    return re.match(URL_REGEX, uri_candidate)


def make_link_headers(further_links):
    """
    Makes the slightly tircky HTTP Link header, if any

    :param further_links: a list of dicts with 'resource', 'rel', & 'anchor' properties, all URIs
    :return: a string
    """
    link_header_content = ''
    count = 0
    for further_link in further_links:
        if not is_a_uri(further_link['anchor']):
            raise PingbackFormulationError('Every anchor in a further_links array must be a valid URI')
        else:
            link_header_content += '<' + further_link['resource'] + '>; ' +\
                                'rel="http://www.w3.org/ns/prov#' + further_link['rel'] + '"; ' +\
                                'anchor="' + further_link['anchor'] + '",'
        count += 1
    return link_header_content[:-1]  # remove last ','


def send_provaq_pingback(pingback_target_uri, uri_list=None, further_links=None):
    """
    Generates and posts a PROV-AQ pingback message

    Messages formulated according to http://www.w3.org/TR/prov-aq/#provenance-pingback, specifically examples 12, 13 & 14
    :param pingback_target_uri: a URI, to where the pingback is sent
    :param uri_list: a list object of URIs
    :param further_links: a list of dicts with 'resource', 'rel', & 'anchor' properties, all URIs
    :return: True or an error message
    """
    import requests

    headers = {'Content-Type': 'text/uri-list'}

    # if further links is set, iterate through them and create appropriate Link headers
    if further_links is not None:
        headers['Link'] = make_link_headers(further_links)

    # join the URIs into a string for the message body
    if uri_list is not None:
        body = '\n'.join(uri_list)  # the standard says CRLF (\r\n), not just \n
    else:
        # if we have no URIs, set the body to None and set a Content-Length header of zero
        body = None
        headers['Content-Length'] = '0'

    # send the post, as per http://www.w3.org/TR/prov-aq/
    try:
        r = requests.post(pingback_target_uri, data=body, headers=headers)
        result = (r.status_code == 204)
        if result:
            return [True]
        else:
            return [False, r.content]
    except Exception as e:
        print(e.message)
        return [False, e.message]


def send_proms_pingback(pingback_target_uri, payload, mimetype='text/turtle'):
    """
    Generates and posts a PROMS pingback message

    :param pingback_target_uri: a URI, to where the pingback is sent
    :param payload: an RDF file, in one of the allowed formats and conformant with the PROMS pingback message spec
    :param mimetype: the mimetype of the RDF file being sent
    :return: True or an error message
    """
    import requests

    headers = {'Content-Type': mimetype}

    # send the post
    try:
        r = requests.post(pingback_target_uri, data=payload, headers=headers)
        result = (r.status_code == 201)
        if result:
            return [True, r.content]
        else:
            return [False, r.content]
    except Exception as e:
        print(e.message)
        return [False, e.message]


def generate_proms_msg_from_report(report_graph, entities_uris, pingback_target_uri, report_type='External'):
    if report_type == 'Basic':
        # we can't generate a Pingback message from a Basic report as there are no Entities defined
        raise PingbackFormulationError('A PROMS Pingback message cannot be generated from a PROMS Basic Report')
    elif report_type == 'External':
        # PROMS pingback message requirements (rules) from http://promsns.org/pingbacks/validator/about

        # For R1: assume that the Report from PROMS is already valid according to PROV-O

        # For R2: add a prov:pingback <pingback_target_uri> for each Entity being pingbacked for
        for entity_uri in entities_uris:
            report_graph.add((URIRef(entity_uri), URIRef('http://www.w3.org/ns/prov#pingback'), URIRef(pingback_target_uri)))

        # For R3: check that each Entity being pingbacked for is prov:used by the sole Activity
        # No need to check for any other conditions as the sole Actvity in an External Report is guarenteed
        for entity_uri in entities_uris:
            a = report_graph.query('''
                                PREFIX prov: <http://www.w3.org/ns/prov#>
                                ASK
                                WHERE {
                                    ?a  a prov:Activity ;
                                        prov:used <''' + entity_uri + '''>
                                }
                                ''')
            if not a:
                raise PingbackFormulationError('The Entity <' + entity_uri + '> is not prov:used by the Enternal Report\'s prov:Activity as required by PROMS pingback message rule R2 (see http://promsns.org/pingbacks/validator/about)')

        return report_graph.serialize(format='turtle')
    else:  # Internal
        print('Internal')


class PingbackFormulationError(Exception):
    def conf(self, *args):
        # *args is used to get a list of the parameters passed in
        self.args = [a for a in args]