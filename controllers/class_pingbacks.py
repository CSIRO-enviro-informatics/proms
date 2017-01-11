from class_incoming import IncomingClass
import cStringIO
import uuid
from rdflib import Graph, URIRef, Literal, Namespace, RDF, XSD
from modules.rulesets.pingbacks import PromsPingback, ProvPingback
import settings
from database import sparqlqueries
from modules.ldapi import LDAPI
from datetime import datetime


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
            print self.request.headers
            conformant_pingback = ProvPingback(self.request)

            # ensure that this Pingback has the URI(s) of the Resource(s) it is for
            if self.request.args.get('resource_uri') is None:
                error_message = 'No resource URI is indicated for this pingback. Pingbacks sent to a PROMS Server ' \
                                'instance must be posted to ' \
                                'http://{POROMS_INTANCE}/function/lodge-pingback?resource_uri={RESOURCE_URI}'
                if self.error_messages is not None:
                    self.error_messages.append(error_message)
                else:
                    self.error_messages = [error_message]

                return False
            elif not LDAPI.is_a_uri(self.request.args.get('resource_uri')):
                error_message = 'The resource URI indicated for this pingback does not validate as a URI'
                if self.error_messages is not None:
                    self.error_messages.append(error_message)
                else:
                    self.error_messages = [error_message]

                return False

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
        # add graph metadata, regardless of the type of Pingback
        # the URI of the Pingback must have been generated before doing this so we can refer to the graph
        PROV = Namespace('http://www.w3.org/ns/prov#')
        DCT = Namespace('http://purl.org/dc/terms/')
        self.graph = Graph()
        self.graph.bind('prov', PROV)
        self.graph.bind('dct', DCT)
        if self.uri is not None:
            # a basic capturing of...
            # ... the date this Pingback was sent to this PROMS Server
            self.graph.add((
                URIRef(self.uri),
                RDF.type,
                PROV.Bundle
            ))
            self.graph.add((
                URIRef(self.uri),
                DCT.dateSubmitted,
                Literal(datetime.now().isoformat(), datatype=XSD.dateTime)
            ))
            # ... who contributed this Pingback
            self.graph.add((
                URIRef(self.uri),
                DCT.contributor,
                URIRef(self.request.remote_addr)
            ))
            # TODO: add other useful metadata variables gleaned from the HTTP message headers

            # PROV Pingbacks can only be of mimtype text/uri-list
            if self.mimetype == 'text/uri-list':
                self._convert_prov_pingback_to_rdf()
            # PROMS Pingbacks can only be of an RDF mimetype
            else:
                self._convert_proms_pingback_to_rdf()
        else:
            raise Exception('The Incoming Pingback must have had a URI generated for it by PROMS Server before the data'
                            'for it is stored. The function determine_uri() generated the URI.')

    def _convert_prov_pingback_to_rdf(self):
        # every URI in the PROV-AQ message is treated as a provenance statement about the resource
        PROV = Namespace('http://www.w3.org/ns/prov#')
        self.graph.bind('prov', PROV)
        for uri_line in self.data.split('\n'):
            self.graph.add((
                URIRef(self.request.args.get('resource_uri')),
                PROV.has_provenance,
                URIRef(uri_line)
            ))

        # if there are Link headers about other resources, create DCT provenance indicators for them too
        if self.request.headers.get('Link'):
            for link_header in self.request.headers.get('Link').split(','):
                uri, rel, anchor = link_header.split(';')
                self.graph.add((
                    URIRef(uri.strip('<>')),
                    URIRef(rel.strip().replace('rel=', '').strip('"')),
                    URIRef(anchor.strip().replace('anchor=', '').strip('"'))
                ))

    def _convert_proms_pingback_to_rdf(self):
        # convert the data to RDF (just de-serialise it)
        self.graph += Graph().parse(data=self.request.data, format=LDAPI.get_rdf_parser_for_mimetype(self.request.mimetype))


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
