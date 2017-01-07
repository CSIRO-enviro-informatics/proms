from class_incoming import IncomingClass
import cStringIO
import uuid
from rdflib import Graph, URIRef
from modules.rulesets.pingbacks import PromsPingback, ProvPingback
import settings
from database import sparqlqueries
from modules.ldapi import LDAPI


class IncomingPingback(IncomingClass):
    acceptable_mimes = LDAPI.get_rdf_mimetypes_list() + ['text/uri-list']

    def __init__(self, request):
        IncomingClass.__init__(self, request.data, request.mimetype)

        self.request = request
        self.pingback_endpoint = request.url

        self.determine_uri()

    def valid(self):
        """Validates an incoming Pingback using direct tests using the Pingbacks RuleSet"""
        # PROV Pingbacks can only be of mimtype text/uri-list
        if self.mimetype == 'text/uri-list':
            conformant_pingback = ProvPingback(self.request)
        # PROMS Pingbacks can only be of an RDF mimetype
        else:
            conformant_pingback = PromsPingback(self.request, self.pingback_endpoint)

        if not conformant_pingback.passed:
            self.error_messages = conformant_pingback.fail_reasons
            return False

        return True

    def determine_uri(self):
        """Gets the URI of the named graph used to store this Pingback's information"""
        # ask PROMS Server for a new Pingbacks URI
        new_uri = settings.PINGBACK_BASE_URI + str(uuid.uuid4())
        self.uri = new_uri

    def convert_pingback_to_rdf(self):
        # PROV Pingbacks can only be of mimtype text/uri-list
        if self.mimetype == 'text/uri-list':
            self._convert_prov_pingback_to_rdf()
        # PROMS Pingbacks can only be of an RDF mimetype
        else:
            self._convert_proms_pingback_to_rdf()

    def _convert_prov_pingback_to_rdf(self):
        # TODO: convert a PROV pingback to RDF
        g = Graph()
        g.add((URIRef('http://fake.com'), URIRef('http://fake2.com'), URIRef('http://fake3.com')))
        self.graph = g  # Graph()  # just use an fake graph for now

    def _convert_proms_pingback_to_rdf(self):
        # convert the data to RDF (just de-serialise it)
        self.graph = Graph().parse(data=self.request.data, format=LDAPI.get_rdf_parser_for_mimetype(self.request.mimetype))


def register_pingback(data):
    """ Register a pingback that has been sent to the system
    """
    g = Graph()
    try:
        g.parse(cStringIO.StringIO(data), format="n3")
    except Exception as e:
        return [False, 'Could not parse pingback: ' + str(e)]
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX dpn-proms: <http://promsns.org/def/dpn-proms#>

        SELECT ?entity ?pq_uri WHERE {
            ?entity a prov:Entity .
            ?p dpn-proms:provenanceQueryUri ?pq_uri
        }
    '''
    query_result = g.query(query)
    for row in query_result:
        if len(row) == 2:
            query = '''
                @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
                @prefix prov: <http://www.w3.org/ns/prov#> .
                @prefix proms: <http://promsns.org/def/proms#> .
                @prefix : <%(DPN_BASE_URI)s#> .

                :x     a proms:LinkingActivity ;
                    prov:used <%(entity)s> ;
                    proms:provenaceQueryUri <%(pq_uri)s>^^xsd:anyUri
                .
            ''' % {
                'DPN_BASE_URI': settings.DPN_BASE_URI,
                'entity': row['entity'],
                'pq_uri': row['pq_uri']
            }
            db_result = sparqlqueries.insert(query)
            if not db_result[0]:
                return [False, 'Problem storing received pingback: ' + db_result[1]]
    return [True]


def send_pingback(report_graph):
    """ Send all pingbacks for the provided Report
    """
    if hasattr(settings, 'PINGBACK_STRATEGIES') and settings.PINGBACK_STRATEGIES:
        for strategy in settings.PINGBACK_STRATEGIES:
            if hasattr(strategy_functions, 'try_strategy_' + str(strategy)):
                strategy_method = getattr(strategy_functions, 'try_strategy_' + str(strategy))
                pingback_result = strategy_method(report_graph)
                if 'pingback_attempt' in pingback_result:
                    attempt = pingback_result['pingback_attempt']
                    if 'pingback_successful' in pingback_result:
                        successful = pingback_result['pingback_successful']
    # TODO: Return attempts and successes if they're to be used
