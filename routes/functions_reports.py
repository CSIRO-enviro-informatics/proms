from rdflib import Graph
import cStringIO
from ldapi import LDAPI
import rulesets.reports as report_rulesets
import functions_sparqldb
import api_functions
import settings
import uuid


class ReportsFunctions:
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
            functions_sparqldb.insert(self.report_graph, self.report_uri)
            return True
        except Exception as e:
            self.error_messages = ['Could not connect to the provenance database']
            return False


def get_reports_dict():
    """ Get details of all Reports
    """
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT DISTINCT ?r ?t
        WHERE {
            GRAPH ?g {
                { ?r a proms:BasicReport . }
                UNION
                { ?r a proms:ExternalReport . }
                UNION
                { ?r a proms:InternalReport . }
                ?r rdfs:label ?t
            }
        }
        ORDER BY ?r
    '''
    reports = functions_sparqldb.query(query)

    report_items = []
    # Check if nothing is returned
    if reports and 'results' in reports:
        for report in reports['results']['bindings']:
            ret = {}
            ret['r'] = urllib.quote(str(report['r']['value']))
            ret['r_u'] = str(report['r']['value'])
            if report.get('t'):
                ret['t'] = str(report['t']['value'])
            report_items.append(ret)
    return report_items


def get_report(report_uri):
    """ Get details for a a Report (JSON)
    """
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?rt ?l ?id ?rs ?rs_t ?sac ?sac_t ?sat ?eac ?eac_t ?eat
        WHERE {
            GRAPH ?g {
                <''' + report_uri + '''> a ?rt .
                <''' + report_uri + '''> rdfs:label ?l .
                <''' + report_uri + '''> proms:nativeId ?id .
                OPTIONAL { <''' + report_uri + '''> proms:reportingSystem ?rs } .
                OPTIONAL { <''' + report_uri + '''> proms:startingActivity ?sac .
                    ?sac prov:startedAtTime ?sat .
                    ?sac rdfs:label ?sac_t
                } .
                OPTIONAL { <''' + report_uri + '''> proms:endingActivity ?eac .
                    ?eac prov:endedAtTime ?eat .
                    ?eac rdfs:label ?eac_t .
                } .
            }
            OPTIONAL { ?rs rdfs:label ?rs_t }
        }
    '''
    return functions_sparqldb.query(query)


def get_report_dict(report_uri):
    """ Get details for a Report (dict)
    """
    report_detail = get_report(report_uri)
    ret = {}
    # Check this
    if report_detail and 'results' in report_detail:
        if len(report_detail['results']['bindings']) > 0:
            index = 0;
            if len(report_detail['results']['bindings']) > 1:
                index = 1;
            ret['l'] = report_detail['results']['bindings'][index]['l']['value']
            ret['t'] = report_detail['results']['bindings'][index]['rt']['value']
            if 'Basic' in ret['t']:
                ret['t_str'] = 'Basic'
            elif 'Internal' in ret['t']:
                ret['t_str'] = 'Internal'
            elif 'External' in ret['t']:
                ret['t_str'] = 'External'
            else:
                ret['t_str'] = 'Unknown Report Type'
            ret['id'] = report_detail['results']['bindings'][index]['id']['value']
            if('rs' in report_detail['results']['bindings'][0]):
                ret['rs'] = urllib.quote(report_detail['results']['bindings'][index]['rs']['value'])
                ret['rs_u'] = report_detail['results']['bindings'][index]['rs']['value']
            if('rs_t' in report_detail['results']['bindings'][0]):
                ret['rs_t'] = report_detail['results']['bindings'][index]['rs_t']['value']
            if('sac' in report_detail['results']['bindings'][0]):
                ret['sac'] = report_detail['results']['bindings'][index]['sac']['value']
                if('sat' in report_detail['results']['bindings'][0]):
                    ret['sat'] = report_detail['results']['bindings'][index]['sat']['value']
                if('sac_t' in report_detail['results']['bindings'][0]):
                    ret['sac_t'] = report_detail['results']['bindings'][index]['sac_t']['value']
            if('eac' in report_detail['results']['bindings'][0]):
                ret['eac'] = report_detail['results']['bindings'][index]['eac']['value']
                if('eat' in report_detail['results']['bindings'][0]):
                    ret['eat'] = report_detail['results']['bindings'][index]['eat']['value']
                if('eac_t' in report_detail['results']['bindings'][0]):
                    ret['eac_t'] = report_detail['results']['bindings'][index]['eac_t']['value']
            ret['uri'] = report_uri
            ret['uri_html'] = urllib.quote(report_uri)
            svg_script = get_report_details_svg(ret)
            if svg_script[0] == True:
                ret['r_script'] = svg_script[1]
    return ret


def get_report_rdf(report_uri):
    """ Get Report details as RDF
    """
    query = '''
        DESCRIBE * WHERE { GRAPH <''' + report_uri + '''> { ?s ?p ?o } FILTER ( ?p != <http://promsns.org/def/proms#reportingSystem> ) }
    '''
    return functions_sparqldb.query_turtle(query)


def get_report_details_svg(report_dict):
    """ Construct the SVG code for a Report
    """
    rLabel = report_dict.get('l', 'uri')
    script = '''
        var rLabel = "''' + rLabel + '''";
        var report = addReport(350, 200, rLabel, "");
    '''
    if report_dict.get('rs'):
        rsLabel = report_dict.get('rs_t', 'uri')
        rsUri = report_dict.get('rs', '')
        if rsUri != '':
            rsUri = settings.WEB_SUBFOLDER + "/id/reportingsystem/?uri=" + rsUri
        script += '''
            var rsLabel = "''' + rsLabel + '''";
            var rsUri = "''' + rsUri + '''";
            var repSystem = addReportingSystem(350, 20, rsLabel, rsUri);
            addLink(report, repSystem, "proms:reportingSystem", RIGHT);
        '''
    if report_dict.get('sac'):
        sac_uri = report_dict.get('sac')
        sac_uri_encoded = urllib.quote(sac_uri)
        sac_label = report_dict.get('sac_t', 'uri')
        script += '''
            var sacUri = "''' + settings.WEB_SUBFOLDER + "/id/activity/?uri=" + sac_uri_encoded + '''";
            var sacLabel = "''' + sac_label + '''";
        '''
        eac_uri = ''
        if report_dict.get('eac'):
            eac_uri = report_dict.get('eac')
            eac_uri_encoded = urllib.quote(eac_uri)
            eac_label = report_dict.get('eac_t', 'uri')
        if sac_uri == eac_uri or eac_uri=='':
            script += '''
                var activity = addActivity(50, 200, sacLabel, sacUri);
                addLink(report, activity, "proms:startingActivity", TOP);
            '''
        elif eac_uri != '':
            script += '''
                var eacUri = "''' + settings.WEB_SUBFOLDER + "/id/activity/?uri=" + eac_uri_encoded + '''";
                var eacLabel = "''' + eac_label + '''";
                var sacActivity = addActivity(50, 120, sacLabel, sacUri);
                addLink(report, sacActivity, "proms:startingActivity", TOP);
                var eacActivity = addActivity(50, 280, eacLabel, eacUri);
                addLink(report, eacActivity, "proms:endingActivity", BOTTOM);
            '''
    return [True, script]


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
            db_result = functions_sparqldb.insert(query)
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
