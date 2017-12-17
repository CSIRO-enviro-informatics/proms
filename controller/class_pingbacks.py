from .class_incoming import IncomingClass
import uuid
from rdflib import Graph, URIRef, Literal, Namespace, RDF, XSD
from modules.rulesets.pingbacks import PromsPingback, ProvPingback
import _config as conf
from modules.ldapi import LDAPI
from datetime import datetime


class IncomingPingback(IncomingClass):
    acceptable_mimes = LDAPI.get_rdf_mimetypes_list() + ['text/uri-list']

    def __init__(self, request):
        IncomingClass.__init__(self, request)

        self.pingback_endpoint = request.url

        self.determine_uri()
        self._generate_named_graph_uri()

    def valid(self):
        """Validates an incoming Pingback using direct _tests using the Pingbacks RuleSet"""
        # PROV Pingbacks can only be of mimtype text/uri-list
        if self.request.mimetype == 'text/uri-list':
            print(self.request.headers)
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
        pass  # no need for this!

    def _generate_named_graph_uri(self):
        self.named_graph_uri = conf.PINGBACK_NAMED_GRAPH_BASE_URI + str(uuid.uuid4())

    def convert_pingback_to_rdf(self):
        # the URI of the Named Graph for this Pingback must have been generated before doing this
        # so we can refer to the graph
        if self.named_graph_uri is not None:
            self.graph = Graph()
            # PROV Pingbacks can only be of mimtype text/uri-list
            if self.request.mimetype == 'text/uri-list':
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

        for uri_line in self.request.data.split('\n'):
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
        PROMS = Namespace('http://promsns.org/def/proms#')
        self.graph.bind('proms', PROMS)

        # type this pingback specifically
        self.graph.add((
            URIRef(self.named_graph_uri),
            RDF.type,
            PROMS.PromsPingback
        ))

        # convert the data to RDF (just de-serialise it)
        self.graph += Graph().parse(
            data=self.request.data,
            format=LDAPI.get_rdf_parser_for_mimetype(self.request.mimetype)
        )

    def generate_named_graph_metadata(self):
        # add graph metadata, regardless of the type of Pingback
        PROV = Namespace('http://www.w3.org/ns/prov#')
        self.graph.bind('prov', PROV)

        PROMS = Namespace('http://promsns.org/def/proms#')
        self.graph.bind('proms', PROMS)

        DCT = Namespace('http://purl.org/dc/terms/')
        self.graph.bind('dct', DCT)

        # ... the date this Pingback was sent to this PROMS Server
        self.graph.add((
            URIRef(self.named_graph_uri),
            DCT.dateSubmitted,
            Literal(datetime.now().isoformat(), datatype=XSD.dateTime)
        ))
        # ... who contributed this Pingback
        self.graph.add((
            URIRef(self.named_graph_uri),
            DCT.contributor,
            URIRef(self.request.remote_addr)
        ))

        # TODO: add other useful metadata variables gleaned from the HTTP message headers

        # PROV Pingbacks can only be of mimtype text/uri-list
        if self.request.mimetype == 'text/uri-list':
            self._generate_prov_pingback_named_graph_metadata()
        else:
            self._generate_proms_pingback_named_graph_metadata()

    def _generate_prov_pingback_named_graph_metadata(self):
        PROMS = Namespace('http://promsns.org/def/proms#')
        self.graph.bind('proms', PROMS)

        # type this pingback specifically
        self.graph.add((
            URIRef(self.named_graph_uri),
            RDF.type,
            PROMS.ProvAqPingbackNamedGraph
        ))

    def _generate_proms_pingback_named_graph_metadata(self):
        PROMS = Namespace('http://promsns.org/def/proms#')
        self.graph.bind('proms', PROMS)

        # type this pingback specifically
        self.graph.add((
            URIRef(self.named_graph_uri),
            RDF.type,
            PROMS.PromsPingbackNamedGraph
        ))
