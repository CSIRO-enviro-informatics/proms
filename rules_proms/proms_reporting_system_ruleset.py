__author__ = 'ayr016'
import sys

sys.path.insert(0, ".\\rules_templates")
sys.path.insert(0, "..\\proms")

from rules_templates import StackedRuleSet
from rules_templates import Rule
import proms_rules as proms_rules

from proms_report_ruleset import PromsReportValid
import settings

class PromsReportingSystemValid(StackedRuleSet):
	def __init__(self, graph):
		ruleset_id = 'proms_reporting_system'
		ruleset_name = 'PROMS Reporting System'
		rules_results = []
		dependencies=[]

		passed = True

		rules_results.append(HasLabel(graph).get_result())
		#rules_results.append(HasValidation(graph).get_result())

		# ToDo: is there an agent, and are they registered on the server?
		# ToDo: is the validation file registered on the server?

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
	"Checks a graph has a label string"
	def __init__(self, report_graph):
		self.rule_id = 'ReportingSystemHasLabel'
		self.rule_name = 'Reporting System Has Label'
		self.rule_business_definition = 'Reporting System must have a label as defined in the PROMS ontology'
		self.rule_authority = 'PROMS-O'
		self.rule_functional_definition = 'Reporting System must have a string rdfs:label object'
		self.component_name = 'PROMS Reporting System Class instance'
		self.passed = True
		self.fail_reasons = []
		self.components_total_count = 1
		self.components_failed_count = 0
		self.failed_components = None

		q=report_graph.query(proms_rules.reporting_system_has_label)
		if not bool(q):
			self.passed = False
			self.fail_reasons.append('The Reporting System class does not contain an rdfs:label')

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

"""
class HasValidation(Rule):
	"Checks a graph has a label string"
	def __init__(self, report_graph):
		self.rule_id = 'ReportingSystemHasValidation'
		self.rule_name = 'Reporting System Has Validation'
		self.rule_business_definition = 'Reporting System must have validation as defined in the PROMS ontology'
		self.rule_authority = 'PROMS-O'
		self.rule_functional_definition = 'Reporting System must have a string proms:validation object'
		self.component_name = 'PROMS Reporting System Class instance'
		self.passed = True
		self.fail_reasons = []
		self.components_total_count = 1
		self.components_failed_count = 0
		self.failed_components = None

		q=report_graph.query(proms_rules.reporting_system_has_validation)
		if not bool(q):
			self.passed = False
			self.fail_reasons.append('The Reporting System class does not contain a validation')

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
"""