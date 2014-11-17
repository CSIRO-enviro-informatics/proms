from conformance.ruleset import RuleSet
from conformance.rule import Rule


class ReportingSystems(RuleSet):
    """
    Rules mandated by the PROMS System for testing ReportingSystem inputs
    """
    def __init__(self, reportingsystem_graph):
        ruleset_id = 'reportingsystem'
        ruleset_name = 'ReportingSystem'
        rules_results = []

        #
        #   Run all the rules
        #
        rules_results.append(HasValidReportingSystem(reportingsystem_graph).get_result())

        #
        #   Call the base RuleSet constructor
        #
        RuleSet.__init__(self,
                         ruleset_id,
                         ruleset_name,
                         'nicholas.car@csiro.au',
                         rules_results)


class HasValidReportingSystem(Rule):

    #Base constructor:
    #   id,                     name,                       business_definition,    authority,
    #   functional_definition,  component_name,             passed,                 fail_reasons,
    #   components_total_count, components_failed_count,    failed_components
    def __init__(self, reportingsystem_graph):
        #
        #   Rule details
        #
        self.rule_id = '1002'
        self.rule_name = 'ReportingSystem Contact'
        self.rule_business_definition = 'To register a ReportingSystem with a PROMS instance, you must supply a contact person for it with an email address, phone number and street address'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'Report graph must contain a VCard contact with email address, phone number and street address'
        self.component_name = 'RDF objects'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 1
        self.components_failed_count = 0
        self.failed_components = None

        #
        #   Rule code
        #
        #has a ReportingSystem class
        qres = reportingsystem_graph.query('''
        PREFIX proms: <http://promsns.org/ns/proms#>
        SELECT ?rs
        WHERE {
          ?rs a proms:ReportingSystem .
        }
        ''')
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('The report does not contain a ReportingSystem class')

        #has a title
        qres = reportingsystem_graph.query('''
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX proms: <http://promsns.org/ns/proms#>
        SELECT ?t
        WHERE {
          ?rs a proms:ReportingSystem .
          ?rs dc:title ?t .
        }
        ''')
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('The ReportingSystem class does not contain a title')

        #has a contact
        qres = reportingsystem_graph.query('''
        PREFIX proms: <http://promsns.org/ns/proms#>
        SELECT ?o
        WHERE {
          ?rs a proms:ReportingSystem .
          ?rs proms:owner ?o .
        }
        ''')
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('The ReportingSystem class does not contain a proms:owner')


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