from class_incoming import IncomingClass
import cStringIO
import uuid
from rdflib import Graph, URIRef, Literal, Namespace, RDF, XSD
from modules.rulesets.pingbacks import PromsPingback, ProvPingback
import settings
from database import queries
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
