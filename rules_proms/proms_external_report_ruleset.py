import sys
from rules_templates import StackedRuleSet
from rules_templates import Rule
import proms_rules as proms_rules
from proms_report_ruleset import PromsReportValid
from proms_basic_report_ruleset import PromsBasicReportValid
from functions_db import *
sys.path.insert(0, ".\\rules_templates")
sys.path.insert(0, "..\\proms")


class PromsExternalReportValid(StackedRuleSet):
    def __init__(self, graph, report_register_uri=None):
        ruleset_id = 'proms_external_report'
        ruleset_name = 'PROMS External Report'
        rules_results = []
        if report_register_uri is None:
            report_register_uri = settings.FUSEKI_QUERY_URI

        dependencies=[]
        r = PromsReportValid(graph).get_result()
        if isinstance(r, list):
            dependencies.extend(r) # extend not append to so as to get [] not [[]]
        else:
            dependencies.append(r)
        #print dependencies
        p = PromsBasicReportValid(graph, report_register_uri)
        dependencies.extend(p.get_result())
        #print dependencies
        passed = True

        # rules are startingActivity == prov:Activity
        # rules are endingActivity == prov:Activity
        # startingActivity and endingActivity *are* the same object
        # >= 1 Entity used
        # >= 1 Entity generated
        rules_results.append(HasStartingActivity(graph).get_result())
        rules_results.append(HasEndingActivity(graph).get_result())
        rules_results.append(HasIdenticalActivities(graph).get_result())
        rules_results.append(HasUsedAndGeneratedEntities(graph).get_result())

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


class HasStartingActivity(Rule):
    def __init__(self, report_graph):
        self.rule_id = 'ReportHasStartingActivity'
        self.rule_name = 'Report Has Starting Activity'
        self.rule_business_definition = 'non-Basic Reports must have a starting activity of type prov:Activity'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'non-Basic report must have a proms:startingActivity of type prov:Activity'
        self.component_name = 'PROMS Report Class instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 1
        self.components_failed_count = 0
        self.failed_components = None

        q=report_graph.query(proms_rules.has_startingActivity)
        if not bool(q):
            self.passed = False
            self.fail_reasons.append('The  Report class does not have a valid starting activity')
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


class HasEndingActivity(Rule):
    def __init__(self, report_graph):
        self.rule_id = 'ReportHasEndingActivity'
        self.rule_name = 'Report Has Ending Activity'
        self.rule_business_definition = 'non-Basic Reports must have an ending activity of type prov:Activity'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'non-Basic report must have a proms:endingActivity of type prov:Activity'
        self.component_name = 'PROMS Report Class instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 1
        self.components_failed_count = 0
        self.failed_components = None

        q=report_graph.query(proms_rules.has_endingActivity)
        if not bool(q):
            self.passed = False
            self.fail_reasons.append('The  Report class does not have a valid ending activity')
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


class HasIdenticalActivities(Rule):
    def __init__(self, report_graph):
        self.rule_id = 'ExternalReportHasIdenticalActivities'
        self.rule_name = 'External Report Has Identical Activities'
        self.rule_business_definition = 'External Reports must have the same activity as startingActivity and endingActivity'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'External report must have proms:endingActivity === proms:startingActivity'
        self.component_name = 'PROMS External Report Class instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 1
        self.components_failed_count = 0
        self.failed_components = None

        q=report_graph.query(proms_rules.are_startingActivityAndEndingActivityTheSame)
        if not bool(q):
            self.passed = False
            self.fail_reasons.append("The External Report Class's starting and ending activities are not the same.")
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


class HasUsedAndGeneratedEntities(Rule):
    def __init__(self, report_graph):
        self.rule_id = 'ExternalReportUsedAndGeneratedEntities'
        self.rule_name = 'External Report Used And Generated Entities'
        self.rule_business_definition = 'External Reports must use and generate at least one entity'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'External report must prov:used a prov:Entity and prov:generate a prov:Entity'
        self.component_name = 'PROMS External Report Class instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 2
        self.components_failed_count = 0
        self.failed_components = None

        q=report_graph.query(proms_rules.used_entity)
        if not bool(q):
            self.passed = False
            self.fail_reasons.append("The External Report Class did not use an entity.")
            self.components_failed_count += 1

        q=report_graph.query(proms_rules.generated_entity)
        if not bool(q):
            self.passed = False
            self.fail_reasons.append("The External Report Class did not generate an entity.")
            self.components_failed_count += 1

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
