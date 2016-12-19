from rdflib import Graph
import cStringIO
from ldapi import LDAPI
import rulesets.pingbacks as pingbacks_rulesets
import functions_sparqldb


class PingbacksFunctions:
    def __init__(self, report_data, report_headers):
        self.report_data = report_data
        self.report_mimetype = report_mimetype
        self.report_graph = None
        self.report_type = None
        self.error_messages = None
        self.report_uri = None

    def valid(self):
        """Validates an incoming Report using direct tests (can it be parsed?) and appropriate RuleSets"""
        # try to parse the Report data
        # TODO: this isn't just RDF
        try:
            self.report_graph = Graph().parse(
                cStringIO.StringIO(self.report_data),
                [item for item in LDAPI.MIMETYPES_PARSERS if item[0] == self.report_mimetype]
            )
        except Exception, e:
            self.error_messages = ['The serialised pingback cannot be parsed',
                                   'Parser says: ' + e.message]
            return False

        # try to determine Report type
        result = self.report_graph.query('''
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
            return  False
        else:
            for row in result:
                self.report_type = row[0]

        # choose RuleSet based on Report type
        if self.report_type == 'BasicReport':
            if __name__ == '__main__':
                conformant_report = report_rulesets

        if not conformant_report.passed:
            self.error_messages = conformant_report.fail_reasons
            return False

        # if the Report has been parsed, we have found the Report type and it's passed it's relevant RuleSet, it's valid
        return True

    def stored(self):
        """ Add a Report to PROMS
        """
        try:
            functions_sparqldb.insert(self.report_graph, self.report_uri)
            return True
        except Exception as e:
            raise
