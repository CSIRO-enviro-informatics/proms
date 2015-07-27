import requests
import settings
import functions
import urllib


PINGBACK_LINK_ONLY_MESSAGE = 0
PINGBACK_PROV_GRAPH_TRANSFER = 1
PINGBACK_PROV_GRAPH_TRANSFER_PLUS_LINK = 2

# TODO: Put in settings..?
pingback_message_type = PINGBACK_LINK_ONLY_MESSAGE


def get_used_entities(report_graph):
    """ Query all of the entities contained in a graph.
    """
    # Get Used Entities
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?e WHERE {
            ?a prov:used ?e .
            { ?e a prov:Entity }
            UNION
            { ?e a proms:ServiceEntity }
        }
    '''
    result = report_graph.query(query)
    return result


# TODO: Deal with DPN_URI
def create_pingback_link_only_message(entity_uri):
    """ Create a basic link-only pingback message.
    """
    message = '''
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        @prefix prov: <http://www.w3.org/ns/prov#> .
        @prefix dpn: <http://purl.org/dpn#> .
        @prefix dpn-proms: <http://promsns.org/def/dpn-proms#> .
        @prefix : <''' + settings.DPN_BASE_URI + '''#> .

        <''' + entity_uri + '''> a dpn:Dataset, prov:Entity .

        :svc a dpn:Service ;
            dpn:hostsDataset :dataset ;
            dpn:implements :my_proms ;
            dpn:endpoint "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''"^^xsd:anyUri ;
            dpn:node    <''' + settings.DPN_BASE_URI + '''> .

        :PromsServiceInterface rdfs:subclassOf dpn:ProvenanceServiceInterface .

        :my_proms    a dpn-proms:PromsServiceInterface ;
            rdfs:subClassOf dpn:ProvenanceServiceInterface ;
            rdfs:label "''' + settings.PROMS_LABEL + '''"^^xsd:string ;
            dpn-proms:provenanceQueryUri "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity?uri=''' + entity_uri + '''"^^xsd:anyUri .
    '''
    return message


# TODO: "Complete actedOnBehalfOf"
def create_provenance_graph_transfer_message(report_graph, entity_uri, rs_uri, rs_label, rs_description):
    """ Create a pingback message for the specified Entity that also contains the Report graph.
    """
    message = '''
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        @prefix proms:   <http://promsns.org/def/proms#> .
        @prefix prov: <http://www.w3.org/ns/prov#> .
        @prefix dpn: <http://purl.org/dpn#> .

        <''' + rs_uri + '''> a proms:ReportingSystem ;
            prov:actedOnBehalfOf "Unknown"  .

        :   a proms:PingBackReport ;
            proms:reportingSystem :rs ;
            rdfs:label "''' + rs_label + '''"^^xsd:string ;
            rdfs:comment "''' + rs_description + '''"^^xsd:string ;
            proms:linkingActivity :linking_activity .

        :linking_activity a proms:LinkingActivity
            prov:used ''' + entity_uri + ''' .

    '''
    message += report_graph
    return message


def create_provenance_graph_transfer_plus_link(report_graph, entity_uri, rs_uri, rs_label, rs_description):
    """ Create a pingback message for the specified Entity that contains the report graph as well as a link.
    """
    message = create_provenance_graph_transfer_message(report_graph, entity_uri, rs_uri, rs_label, rs_description)
    # TODO: Add link
    message += '''
        #    Sending system - optional
        :svc a dpn:Service ;
            dpn:hostsDataset :dataset ;
            dpn:implements :my_proms ;
            dpn:endpoint "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''"^^xsd:anyUri ;
            dpn:node    <''' + settings.DPN_BASE_URI + '''> .

        :PromsServiceInterface rdfs:subclassOf dpn:ProvenanceServiceInterface .

        :my_proms    a dpn-proms:PromsServiceInterface ;
            rdfs:subClassOf dpn:ProvenanceServiceInterface ;
            rdfs:label "''' + settings.PROMS_LABEL + '''"^^xsd:string ;
            dpn-proms:provenanceQueryUri "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity?uri=''' + entity_uri + '''"^^xsd:anyUri .
    '''
    return message


def create_pingback_message(entity_uri, report_graph):
    """ Create a pingback for the specified Entity.
    """
    if pingback_message_type == PINGBACK_LINK_ONLY_MESSAGE:
        return create_pingback_link_only_message(entity_uri)
    elif pingback_message_type == PINGBACK_PROV_GRAPH_TRANSFER or pingback_message_type == PINGBACK_PROV_GRAPH_TRANSFER_PLUS_LINK:
        # Get reporting system details
        query = '''
            PREFIX proms: <http://promsns.org/def/proms#>
            SELECT ?rs WHERE {
                    ?r proms:reportingSystem ?rs .
            }
        '''
        result = report_graph.query(query)
        rs_uri = ''
        for row in result:
            if len(row) > 0:
                rs_uri = row[0]
        rs_dict = functions.get_reportingsystem_dict(rs_uri)
        rs_label = rs_dict.get('t', '')
        # TODO Make sure this exists
        rs_description = rs_dict.get('d', '')

        # Message based on specified message type
        if pingback_message_type == PINGBACK_LINK_ONLY_MESSAGE:
            return create_pingback_link_only_message(entity_uri)
        elif pingback_message_type == PINGBACK_PROV_GRAPH_TRANSFER:
            return create_provenance_graph_transfer_message(report_graph, entity_uri, rs_uri, rs_label, rs_description)
        elif pingback_message_type == PINGBACK_PROV_GRAPH_TRANSFER_PLUS_LINK:
            return create_provenance_graph_transfer_plus_link(report_graph, entity_uri, rs_uri, rs_label, rs_description)


def known_stores(report_graph):
    """ Send pingback for all Entities with the Report graph to known stores
    """
    if settings.KNOWN_PROMS_INSTANCES and len(settings.KNOWN_PROMS_INSTANCES) > 0:
        proms_stores = settings.KNOWN_PROMS_INSTANCES
        entities = get_used_entities(report_graph)
        for row in entities:
            entity_uri = row[0]
            for store in proms_stores:
                if not store.endswith('\\') and not store.endswith('/'):
                    store += '/'
                proms_entity_uri = store + 'id/entity?uri=' + urllib.quote(entity_uri)
                r = requests.get(proms_entity_uri)
                # Success
                if r.status_code == 200:
                    pingback_uri = store + 'function/receive_pingback'
                    message = create_pingback_message(entity_uri, report_graph)
                    r = requests.post(pingback_uri, data=message)
                    if r.status_code != 200:
                        return [False, "Unable to send pingback message: " + message]
        return [True]
    else:
        return [False, 'No PROMS instances could be found in settings (KNOWN_PROMS_INSTANCES)']


# TODO: What to do on success?
def follow_linked_data(report_graph):
    """ Send pingback for all Entities with the Report graph by following linked data
    """
    entities = get_used_entities(report_graph)
    for row in entities:
        entity_uri = row[0]
        guess_uri = entity_uri + '?_view=prov_pingback'
        r = requests.get(entity_uri)
        if r.status_code == 200:
            continue
        guess_uri = entity_uri + '?_view=provenance'
        r = requests.get(entity_uri)
        if r.status_code == 200:
            continue


"""
To add a custom pingback method:

Create a method in this file that takes the incoming report graph as an argument.
For example:

def custom_pingback_method(report_graph):
    # Pingback method code here


Add the method to the list of pingback strategies in settings.py, e.g:

PINGBACK_CONFIG = {
    'pingback_strategies': ['custom_pingback_method', 'known_stores', 'follow_linked_data']
}


Strategies are attempted in the order that they are listed. If one strategy fails, the next
is tried. If only one strategy is needed, make sure it's the only one in the list, e.g:

PINGBACK_CONFIG = {
    'pingback_strategies': ['custom_pingback_method']
}
"""