from class_incoming import IncomingClass
import cStringIO
import uuid
from rdflib import Graph
import api_functions
import modules.rulesets.reports as report_rulesets
import settings
from modules.ldapi import LDAPI


class IncomingReport(IncomingClass):
    def __init__(self, data, mimetype):
        IncomingClass.__init__(self, data, mimetype)

        self.type = None

    def valid(self):
        """Validates an incoming Report using direct tests (can it be parsed?) and appropriate RuleSets"""
        # try to parse the Report data
        try:
            self.graph = Graph().parse(
                cStringIO.StringIO(self.data),
                format=[item[1] for item in LDAPI.MIMETYPES_PARSERS if item[0] == self.mimetype][0]
            )
        except Exception, e:
            self.error_messages = ['The serialised data cannot be parsed. Is it valid RDF?',
                                   'Parser says: ' + e.message]
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
        new_uri = settings.REPORT_BASE_URI + str(uuid.uuid4())
        self.uri = new_uri
        # add that new URI to the in-memory graph
        api_functions.replace_uri(self.graph, old_uri, new_uri)
