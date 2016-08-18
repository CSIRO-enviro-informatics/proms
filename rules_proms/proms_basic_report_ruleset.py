__author__ = 'ayr016'
import sys
from rules_templates import StackedRuleSet
from rules_templates import Rule
import proms_rules as proms_rules
from proms_report_ruleset import PromsReportValid
from functions_db import *
sys.path.insert(0, ".\\rules_templates")
sys.path.insert(0, "..\\proms")


class PromsBasicReportValid(StackedRuleSet):
    def __init__(self, graph, report_register_uri=None):
        ruleset_id = 'proms_basic_report'
        ruleset_name = 'PROMS Basic Report'
        rules_results = []
        if report_register_uri is None:
            report_register_uri = settings.SPARQL_QUERY_URI

        dependencies=[]
        p=PromsReportValid(graph)
        dependencies.append(p.get_result())

        passed = True

        rules_results.append(HasLabel(graph).get_result())
        rules_results.append(HasGeneratedAtTime(graph).get_result())
        rules_results.append(HasReportingSystem(graph, report_register_uri).get_result())
        rules_results.append(HasNativeId(graph).get_result())

        for rules_result in rules_results:
            if not rules_result['passed']:
                passed = False
                break

        StackedRuleSet.__init__(
            self,
            ruleset_id,
            ruleset_name,
            'Melanie Ayre (melanie.ayre@csiro.au)',
            rules_results,
            passed,
            dependencies)


class HasLabel(Rule):
    """Checks a graph has a label string"""
    def __init__(self, report_graph):
        self.rule_id = 'ExternalReportHasLabel'
        self.rule_name = 'External Report Has Label'
        self.rule_business_definition = 'External Reports must have a label as defined in the PROMS ontology'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'External report must have a string rdfs:label object'
        self.component_name = 'PROMS External Report Class instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 1
        self.components_failed_count = 0
        self.failed_components = None

        q = report_graph.query(proms_rules.has_label)
        if not bool(q):
            self.passed = False
            self.fail_reasons.append('The External Report class does not contain an rdfs:label')

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


class HasGeneratedAtTime(Rule):
    """Checks a graph has datetime indicating when the report was generated - separate from the activities"""
    def __init__(self, report_graph):
        self.rule_id = 'BasicReportHasGeneratedAtTime'
        self.rule_name = 'Basic Report Has Generated At Time'
        self.rule_business_definition = 'Basic Reports must have a date time describing when they were generated, as required by the PROMS ontology'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'Basic report must have a datetime rdfs:label object'
        self.component_name = 'PROMS Basic Report Class instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 1
        self.components_failed_count = 0
        self.failed_components = None

        q = report_graph.query(proms_rules.has_generatedAtTime)
        if not bool(q):
            self.passed = False
            self.fail_reasons.append('The Basic Report class does not contain a prov:generatedAtTime')

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


class HasNativeId(Rule):
    def __init__(self, report_graph):
        self.rule_id = 'ReportHasNativeId'
        self.rule_name = 'Report Has A Native ID'
        self.rule_business_definition = 'All Reports must have a nativeId that is an ID for the report instance recognised by the Reporting System'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'Reports must have a proms:nativeId string value'
        self.component_name = 'PROMS Report Class instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 1
        self.components_failed_count = 0
        self.failed_components = None

        q = report_graph.query(proms_rules.has_nativeId)
        if not bool(q):
            self.passed = False
            self.fail_reasons.append('The  Report class does not have a valid proms:nativeId')
            self.components_failed_count = 1

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


class HasReportingSystem(Rule):
    """"Checks that there is a URI for a reporting system, registered on this instance"""
    def __init__(self, report_graph, report_register_uri=None):
        self.rule_id = 'BasicReportHasReportingSystem'
        self.rule_name = 'Basic Report Has Reporting System'
        self.rule_business_definition = 'Basic Reports must have a reporting system as defined in the PROMS ontology'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'Basic report must have a proms:reportingSystem object'
        self.component_name = 'PROMS Basic Report Class instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 1
        self.components_failed_count = 0
        self.failed_components = None

        q = report_graph.query(proms_rules.has_reportingSystem)
        if not bool(q):
            self.passed = False
            self.fail_reasons.append('The Report class does not contain a proms:reportingSystem')

        if report_register_uri is not None:

            # check the reporting system is registered on the report register
            reporting_system = report_graph.query(proms_rules.get_reportingSystem)
            for r in reporting_system:
                query = proms_rules.has_registered_reportingSystem(r[0])
                response = db_query_secure(query)

                if response['boolean'] is False:
                    self.passed = False
                    self.fail_reasons.append('The Report class does not refer to a valid reporting system')

        else:
            self.passed = False
            self.fail_reasons.append('Cannot test if reporting system is registered as no report register has been provided')

        if not self.passed:
            self.components_failed_count = 1

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

    def reporting_system_registered(self, graph, text):
        try:
            reportingSystem = graph.query(proms_rules.get_reportingSystem)[0]
        except:
            reportingSystem = None

        if reportingSystem is not None:
                return (reportingSystem in text, reportingSystem, text)
        else:
            return (False, "(not specified)", text)