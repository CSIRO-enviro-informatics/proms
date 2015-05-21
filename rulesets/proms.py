from conformance.ruleset import RuleSet
from conformance.rule import Rule


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
        #g = Graph().parse(data=report, format='turtle')
        g = report

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
            self.fail_reasons.append('The Report class does not contain a rdfs:label')

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

        # XXX Changed reportingSystem to ReportingSystemUri
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
            ?s  proms:reportingSystem ?rs .
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


# TODO: check the Activity(ies) are correct
class ReportAppropriateActivities(Rule):
    pass


# TODO: RS is a property of Report so merge this with 1st rule
class ReportHasAValidReportingSystem(Rule):
    #the RS needs to be on this PROMS instance
    #if it is, we can assume it's valid since it got past its own validation on the way in
    pass


# TODO: RS is a property of Report so merge with, or call from?, 1st rule
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
        PREFIX proms: <http://promsns.org/def/proms#>
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
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?t
        WHERE {
          ?rs a proms:ReportingSystem .
          ?rs rdfs:label ?t .
        }
        ''')
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('The ReportingSystem class does not contain a title')

        #has a contact
        qres = reportingsystem_graph.query('''
        PREFIX proms: <http://promsns.org/def/proms#>
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