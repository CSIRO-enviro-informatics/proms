from conformance.ruleset import RuleSet
from conformance.rule import Rule


class Proms(RuleSet):
    """
    Rules mandated by the PROMS Ontology
    """
    def __init__(self, report_graph):
        ruleset_id = 'proms'
        ruleset_name = 'PROMS'
        rules_results = []

        #
        #   Run all the rules
        #
        rules_results.append(HasReport(report_graph).get_result())

        #
        #   Call the base RuleSet constructor
        #
        RuleSet.__init__(self,
                         ruleset_id,
                         ruleset_name,
                         'nicholas.car@csiro.au',
                         rules_results)


class HasReport(Rule):

    #Base constructor:
    #   id,                     name,                       business_definition,    authority,
    #   functional_definition,  component_name,             passed,                 fail_reasons,
    #   components_total_count, components_failed_count,    failed_components
    def __init__(self, report_graph):
        #
        #   Rule details
        #
        self.rule_id = '1001'
        self.rule_name = 'Report contains PROMS-O Report'
        self.rule_business_definition = 'Reports must contain a PROMS-O Report class with certain properties'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'Report graph must return a proms:Report class or subclass with properties of cardinality 1'
        self.component_name = 'Report'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 1
        self.components_failed_count = 0
        self.failed_components = None

        #
        #   Rule code
        #
        #has a Report class
        qres = report_graph.query('''
        PREFIX proms: <http://promsns.org/ns/proms#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?s
        WHERE {
            ?s  a            proms:Report .
        }
        ''')
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('The report does not contain a Report class')

        #has a title
        qres = report_graph.query('''
        PREFIX proms: <http://promsns.org/ns/proms#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?s
        WHERE {
            ?s  a            proms:Report .
            ?s  dc:title     ?t .
        }
        ''')
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('The report\'s Report class does not contain a dc:title')

        #has a jobId
        qres = report_graph.query('''
        PREFIX proms: <http://promsns.org/ns/proms#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?s
        WHERE {
            ?s  a            proms:Report .
            ?s  proms:jobId  ?j .
        }
        ''')
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('The report\'s Report class does not contain a proms:jobId')


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


class ReportAppropriateActivities(Rule):
    pass

