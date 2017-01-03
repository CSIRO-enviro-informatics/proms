import cStringIO
import uuid
from rdflib import Graph
import api_functions
import modules.rulesets.reports as report_rulesets
import settings
from database import sparqlqueries
from modules.ldapi import LDAPI


class IncomingReport:
    def __init__(self, report_data, report_mimetype):
        self.report_data = report_data
        self.report_mimetype = report_mimetype
        self.report_graph = None
        self.report_type = None
        self.error_messages = None
        self.report_uri = None

    def valid(self):
        """Validates an incoming Report using direct tests (can it be parsed?) and appropriate RuleSets"""
        # try to parse the Report data
        try:
            self.report_graph = Graph().parse(
                cStringIO.StringIO(self.report_data),
                format=[item[1] for item in LDAPI.MIMETYPES_PARSERS if item[0] == self.report_mimetype][0]
            )
        except Exception, e:
            self.error_messages = ['The serialised data cannot be parsed. Is it valid RDF?',
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
                self.report_type = str(row[0])

        # choose RuleSet based on Report type
        if self.report_type == 'http://promsns.org/def/proms#BasicReport':
            conformant_report = report_rulesets.BasicReport(self.report_graph)
        elif self.report_type == 'http://promsns.org/def/proms#ExternalReport':
            conformant_report = report_rulesets.ExternalReport(self.report_graph)
        else:  # self.report_type == 'InternalReport':
            conformant_report = report_rulesets.InternalReport(self.report_graph)

        if not conformant_report.passed:
            self.error_messages = conformant_report.fail_reasons
            return False

        # if the Report has been parsed, we have found the Report type and it's passed it's relevant RuleSet, it's valid
        return True

    def determine_report_uri(self):
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
        for r in self.report_graph.query(q):
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
            for r in self.report_graph.query(q):
                self.report_uri = r['uri']

        return True

    def _generate_new_uri(self, old_uri):
        # ask PROMS Server for a new Report URI
        new_uri = settings.REPORT_BASE_URI + str(uuid.uuid4())
        self.report_uri = new_uri
        # add that new URI to the in-memory graph
        api_functions.replace_uri(self.report_graph, old_uri, new_uri)

    def stored(self):
        """ Add a Report to PROMS
        """
        try:
            sparqlqueries.insert(self.report_graph, self.report_uri)
            return True
        except Exception as e:
            self.error_messages = ['Could not connect to the provenance database']
            return False


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

        SELECT ?s ?uri WHERE {
            ?s a prov:Entity .
            ?p dpn-proms:provenanceQueryUri ?uri
        }
    '''
    query_result = g.query(query)
    for row in query_result:
        if len(row) == 2:
            query = '''
                @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
                @prefix prov: <http://www.w3.org/ns/prov#> .
                @prefix proms: <http://promsns.org/def/proms#> .
                @prefix : <''' + settings.DPN_BASE_URI + '''#> .

                :x     a proms:LinkingActivity ;
                prov:used <''' + row[0] + '''> ;
                proms:provenaceQueryUri <''' + row[1] + '''>^^xsd:anyUri .
            '''
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


def create_report_formparts(form_parts_json_obj):
    # agent-new-existing [new, existing]
    #   - agent (URI)
    #   - agent-name, agent-URI, agent-email

    # report-type [BasicReport, ExternalReport]
    # report-title
    # report-reportingsystem (URI-encoded)
    # report-nativeId

    # activity-title
    # activity-description
    # activity-startedAtTime
    # activity-endedAtTime

    pass
