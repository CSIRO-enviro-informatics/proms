__author__ = 'ayr016'
import sys

sys.path.insert(0, ".\\rules_templates")
sys.path.insert(0, "..\\proms")

from rules_templates import StackedRuleSet
from rules_templates import Rule
import proms_rules as proms_rules

# from proms_report_ruleset import PromsReportValid
# from proms_basic_report_ruleset import PromsBasicReportValid
from proms_external_report_ruleset import PromsExternalReportValid
import settings
from functions_db import *
import requests

class vhirl_report(StackedRuleSet):
    def __init__(self, graph, report_register_uri=None):
        ruleset_id = 'vhirl_report'
        ruleset_name = 'VHIRL Report'
        rules_results = []
        if report_register_uri is None:
            report_register_uri = settings.SPARQL_QUERY_URI

        dependencies=[]

        dependencies.extend(PromsExternalReportValid(graph, report_register_uri).get_result())

        passed = True
        # put rules_results here
        rules_results.append(HasUser(graph).get_result())
        rules_results.append(HasDuration(graph).get_result())
        rules_results.append(UsesSolution(graph).get_result())

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

class HasUser(Rule):
    def __init__(self, report_graph):
        self.rule_id = 'VHIRLReportHasValidAssociate'
        self.rule_name = 'VHIRL Report has valid associate.'
        self.rule_business_definition = 'All VHIRL reports must have a valid associated user.'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'All VHIRL reports must hav a prov:wasAssociatedWith value which is an accessible url.'
        self.component_name = 'VHIRL Report instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 3
        self.components_failed_count = 0
        self.failed_components = None

        query = '''
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT ?user
            WHERE {
            ?s  a            proms:ExternalReport .
            ?s proms:startingActivity ?act .
            ?act prov:wasAssociatedWith ?user .
                }
            '''

        users = report_graph.query(query)

        if len(users) > 1:
            self.passed = False
            self.fail_reasons.append("VHIRL reports can only have one user.")
            self.components_failed_count += 1


        for user in users:
            user_uri = user[0]
            if user_uri[0:4] != 'http':
                print user_uri[0:4]
                self.passed = False
                self.fail_reasons.append("The user URI must be a URL.")
                self.components_failed_count += 1
                continue
            if not requests.get(user_uri).status_code == requests.codes.ok:
                self.passed = False
                self.fail_reasons.append("The user URI must be valid.")
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

class HasDuration(Rule):
    """ All VHIRL Reports are expected to have a start and end time, and the end
    time must be strictly after the start time. """
    def __init__(self, report_graph):
        self.rule_id = 'VHIRLReportHasPositiveDuration'
        self.rule_name = 'VHIRL Report has positive duration'
        self.rule_business_definition = 'VHIRL reports must have taken a positive amount of time.'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'The prov:startedAtTime must be before prov:endedAtTime, they cannot be the same.'
        self.component_name = 'VHIRL Report instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 2
        self.components_failed_count = 0
        self.failed_components = None

        query = '''
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT ?startedAt ?endedAt
            WHERE {
            ?s  a            proms:ExternalReport .
            ?s proms:startingActivity ?act .
            ?act prov:startedAtTime ?startedAt .
            ?act prov:endedAtTime ?endedAt .
                }
            '''

        timings = report_graph.query(query)

        for row in timings:
            if len(row) < 2:
                self.passed = False
                self.fail_reasons.append("VHIRL report activities must have a start and end time.")
                self.components_failed_count += 1
                continue

            if row.startedAt >= row.endedAt:
                self.passed = False
                self.fail_reasons.append("VHIRL report activities must end after they started. They cannot be instantaneous.")
                self.components_failed_count += 1
                continue

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


class UsesSolution(Rule):
    """ All VHIRL Reports are expected to use a Solution 
    from the Solution Centre. """
    def __init__(self, report_graph):
        self.rule_id = 'VHIRLReportHasSolution'
        self.rule_name = 'VHIRL report has solution'
        self.rule_business_definition = 'A VHIRL report must have an associated Solution Centre Solution.'
        self.rule_authority = 'PROMS-O'
        self.rule_functional_definition = 'One of the Entities in prov:Used must be a URI referring to an instance of the SSSC.'
        self.component_name = 'VHIRL Report instance'
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 3
        self.components_failed_count = 0
        self.failed_components = None

        query = '''
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT ?input
            WHERE {
            ?s  a            proms:ExternalReport .
            ?s proms:startingActivity ?act .
            ?act prov:used ?input .
                }
            '''

        inputs = report_graph.query(query)
        found_solution = False

        for row in inputs:
            if len(row) < 1:
                self.passed = False
                self.fail_reasons.append("VHIRL report must have at least one input.")
                self.components_failed_count += 1
                continue

            for input_entity in row:
                if input_entity[0:4] != 'http':
                    self.passed = False
                    self.fail_reasons.append("The input Entity must be a url.")
                    self.components_failed_count += 1
                    continue

                if "scm/solutions" in str(input_entity):
                    found_solution = True

        if not found_solution:
            self.passed = False
            self.fail_reasons.append("There must be at least on input Entity which is a SSSC Solution.")
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
