from rules_templates import RuleSet, Rule
from rdflib import Graph


class PromsReport(RuleSet):
    """
    Rules mandated by the PROMS Ontology
    """
    def __init__(self, report):
        ruleset_id = 'proms'
        ruleset_name = 'PROMS'
        passed = True
        rules_results = []

        # make a Graph from the string or file
        if isinstance(report, Graph):
            g = report
        else:
            g = Graph().parse(data=report, format='turtle')

        #
        #   Run all the rules
        #
        rules_results.append(ReportClassValidProperties(g).get_result())

        # calculate if RuleSet passed
        for rule in rules_results:
            if not rule['passed']:
                passed = False

        #
        #   Call the base RuleSet constructor
        #
        RuleSet.__init__(self,
                         ruleset_id,
                         ruleset_name,
                         'nicholas.car@csiro.au',
                         rules_results,
                         passed)


# TODO change this to check for only the Report class' properties
class ReportClassValidProperties(Rule):

    #Base constructor:
    #   id,                     name,                       business_definition,    authority,
    #   functional_definition,  component_name,             passed,                 fail_reasons,
    #   components_total_count, components_failed_count,    failed_components
    def __init__(self, report_graph):
        #
        #   Rule details
        #
        self.rule_id = 'ReportClass'
        self.rule_name = 'Report Class has valid properties'
        self.rule_business_definition = 'Reports Class objects must contain certain properties set out in the PROMS Ontology'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'Report graph must contain a proms:Report class or subclass with correct properties'
        self.component_name = 'PROMS Report Class instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 1
        self.components_failed_count = 0
        self.failed_components = None

        #
        #   Rule code
        #
        # has a Report class
        qres = report_graph.query('''
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?s
        WHERE {
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
        }
        ''')
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('The report does not contain a Report class or subclass')

        # has a title
        qres = report_graph.query('''
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?s
        WHERE {
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  rdfs:label     ?t .
        }
        ''')
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('The Report class does not contain a dc:title')

        # has a nativeId
        qres = report_graph.query('''
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?s
        WHERE {
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  proms:nativeId  ?j .
        }
        ''')
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('The Report class does not contain a proms:nativeId')

        # has a ReportingSystem
        qres = report_graph.query('''
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?s
        WHERE {
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  proms:reportingSystem  ?rs .
        }
        ''')
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('The Report class does not contain a proms:reportingSystem')


        #
        #   Call the base Rule constructor
        #
        Rule.__init__(self,
                      self.rule_id,
                      self.rule_name,
                      self.rule_business_definition,
                      self.rule_authority,
                      self.rule_functional_definition,
                      self.component_name,
                      self.passed,
                      self.fail_reasons,
                      self.components_total_count,
                      self.components_failed_count,
                      self.failed_components)


