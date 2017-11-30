from .class_incoming import IncomingClass
import io
import uuid
from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD
import controller.api_functions as api_functions
import modules.rulesets.reports as report_rulesets
from _config import __init__
from modules.ldapi import LDAPI
from datetime import datetime


class IncomingReport(IncomingClass):
    def __init__(self, request):
        IncomingClass.__init__(self, request)

        self.type = None
        self._generate_named_graph_uri()

    def valid(self):
        """Validates an incoming Report using direct _tests (can it be parsed?) and appropriate RuleSets"""
        # try to parse the Report data
        try:
            self.graph = Graph().parse(
                io.StringIO(self.request.data),
                format=[item[1] for item in LDAPI.MIMETYPES_PARSERS if item[0] == self.request.mimetype][0]
            )
        except Exception as e:
            self.error_messages = ['The serialised data cannot be parsed. Is it valid RDF?',
                                   'Parser says: ' + str(e)]
            return False

        # try to determine Report type
        result = self.graph.query('''
             PREFIX proms: <http://promsns.org/def/proms#>
             SELECT DISTINCT ?type WHERE {
                 ?r a ?type .
                 FILTER (?type = proms:BasicReport || ?type = proms:ExternalReport || ?type = proms:InternalReport)
             }
         ''')
        if len(result) != 1:
            self.error_messages = [
                    'Could not determine Report type. Must be one of proms:BasicReport, proms:ExternalReport or '
                    'proms:InternalReport'
            ]
            return False
        else:
            for row in result:
                self.type = str(row[0])

        # choose RuleSet based on Report type
        if self.type == 'http://promsns.org/def/proms#BasicReport':
            conformant_report = report_rulesets.BasicReport(self.graph)
        elif self.type == 'http://promsns.org/def/proms#ExternalReport':
            conformant_report = report_rulesets.ExternalReport(self.graph)
        else:  # self.report_type == 'InternalReport':
            conformant_report = report_rulesets.InternalReport(self.graph)

        if not conformant_report.passed:
            self.error_messages = conformant_report.fail_reasons
            return False

        # if the Report has been parsed, we have found the Report type and it's passed it's relevant RuleSet, it's valid
        return True

    def determine_uri(self):
        """Determines the URI for this Report"""
        # TODO: replace these two SPARQL queries with one, use the inverse of the "placeholder" find
        # if this Report has a placeholder URI, generate a new one
        q = '''
            SELECT ?uri
            WHERE {
                { ?uri a <http://promsns.org/def/proms#BasicReport> . }
                UNION
                { ?uri a <http://promsns.org/def/proms#ExternalReport> . }
                UNION
                { ?uri a <http://promsns.org/def/proms#InternalReport> . }
                FILTER regex(str(?uri), "placeholder")
            }
        '''
        uri = None
        for r in self.graph.query(q):
            uri = r['uri']

        if uri is not None:
            self._generate_new_uri(uri)
        else:
            # since it has an existing URI, not a placeholder one, use the existing one
            q = '''
                SELECT ?uri
                WHERE {
                    { ?uri a <http://promsns.org/def/proms#BasicReport> . }
                    UNION
                    { ?uri a <http://promsns.org/def/proms#ExternalReport> . }
                    UNION
                    { ?uri a <http://promsns.org/def/proms#InternalReport> . }
                }
            '''
            for r in self.graph.query(q):
                self.uri = r['uri']

        return True

    def _generate_new_uri(self, old_uri):
        # ask PROMS Server for a new Report URI
        new_uri = __init__.REPORT_BASE_URI + str(uuid.uuid4())
        self.uri = new_uri
        # add that new URI to the in-memory graph
        api_functions.replace_uri(self.graph, old_uri, new_uri)

    def _generate_named_graph_uri(self):
        self.named_graph_uri = __init__.REPORT_NAMED_GRAPH_BASE_URI + str(uuid.uuid4())

    def generate_named_graph_metadata(self):
        PROV = Namespace('http://www.w3.org/ns/prov#')
        self.graph.bind('prov', PROV)

        PROMS = Namespace('http://promsns.org/def/proms#')
        self.graph.bind('proms', PROMS)

        DCT = Namespace('http://purl.org/dc/terms/')
        self.graph.bind('dct', DCT)

        self.graph.add((
            URIRef(self.named_graph_uri),
            RDF.type,
            PROMS.ReportNamedGraph
        ))

        # ... the date this Report was sent to this PROMS Server
        self.graph.add((
            URIRef(self.named_graph_uri),
            DCT.dateSubmitted,
            Literal(datetime.now().isoformat(), datatype=XSD.dateTime)
        ))

        # ... who contributed this Report
        self.graph.add((
            URIRef(self.named_graph_uri),
            DCT.contributor,
            URIRef(self.request.remote_addr)
        ))
