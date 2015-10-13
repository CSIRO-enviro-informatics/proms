__author__ = 'ayr016'
import sys

sys.path.insert(0, ".\\rules_templates")
sys.path.insert(0, "..\\proms")

from rules_templates import StackedRuleSet
from rules_templates import Rule
import proms_rules as proms_rules

from proms_report_ruleset import PromsReportValid
from proms_basic_report_ruleset import PromsBasicReportValid
from proms_external_report_ruleset import HasStartingActivity
from proms_external_report_ruleset import HasEndingActivity
from proms_external_report_ruleset import HasUsedAndGeneratedEntities
import settings
from functions_db import *

class PromsInternalReportValid(StackedRuleSet):
	def __init__(self, graph, report_register_uri=None):
		ruleset_id = 'proms_internal_report'
		ruleset_name = 'PROMS Internal Report'
		rules_results = []
		if report_register_uri is None:
			report_register_uri = settings.FUSEKI_QUERY_URI

		dependencies=[]
		r=PromsReportValid(graph).get_result()
		if isinstance(r, list):
			dependencies.extend(r) # extend not append to so as to get [] not [[]]
		else:
			dependencies.append(r)
		print dependencies
		p=PromsBasicReportValid(graph, report_register_uri)
		dependencies.extend(p.get_result())
		print dependencies
		passed = True

		# (startingActivity != endingActivity) MUST be prov:Activity   !!!!!! This means that Internal can't depend on External
		# startedAtTime of startingActivity < startedAtTime of endingActivity
		# >= 1 Entity used not also generated in same Report
		# >= 1 Entity generated not also used in same Report

		# need to add IsInternalReport
		rules_results.append(HasStartingActivity(graph).get_result())
		rules_results.append(HasEndingActivity(graph).get_result())
		rules_results.append(HasDifferentActivities(graph).get_result())
		rules_results.append(StartedStartActivityBeforeStartedEndActivity(graph).get_result())
		rules_results.append(HasUsedAndGeneratedEntities(graph).get_result())
		rules_results.append(EntityUsedNotGenerated(graph).get_result())

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

class HasDifferentActivities(Rule):
	def __init__(self, report_graph):
		self.rule_id = 'InternalReportHasDifferentActivities'
		self.rule_name = 'Internal Report Has Different Activities'
		self.rule_business_definition = 'Internal Reports must have different activities as startingActivity and endingActivity'
		self.rule_authority = 'PROMS-O'
		self.rule_functional_definition = 'Internal report must have proms:endingActivity != proms:startingActivity'
		self.component_name = 'PROMS Internal Report Class instance'
		self.passed = True
		self.fail_reasons = []
		self.components_total_count = 1
		self.components_failed_count = 0
		self.failed_components = None

		q=report_graph.query(proms_rules.are_startingActivityAndEndingActivityDifferent)
		if not bool(q):
			self.passed = False
			self.fail_reasons.append("The Internal Report Class's starting and ending activities are the same.")
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

class StartedStartActivityBeforeStartedEndActivity(Rule):
	def __init__(self, report_graph):
		self.rule_id = 'InternalReportStartActivityStartedBeforeEndActivityStarted'
		self.rule_name = 'Internal Report StartActivity starts before EndActivity Starts'
		self.rule_business_definition = 'Internal Reports startingActivity must start before endingActivity'
		self.rule_authority = 'PROMS-O'
		self.rule_functional_definition = 'Internal report proms:startingActivity prov:startedAtTime must be before proms:endingActivity prov:startedAtTime'
		self.component_name = 'PROMS Internal Report Class instance'
		self.passed = True
		self.fail_reasons = []
		self.components_total_count = 1
		self.components_failed_count = 0
		self.failed_components = None

		q=report_graph.query(proms_rules.started_startActivityBeforeEndActivity)
		if not bool(q):
			self.passed = False
			self.fail_reasons.append("The Internal Report Class's ending activity starts before (or at the same time as) the starting activity starts.")
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

class EntityUsedNotGenerated(Rule):
	def __init__(self, report_graph):
		self.rule_id = 'EntityUsedNotGenerated'
		self.rule_name = 'Internal Report Uses an Entity it does not Generate'
		self.rule_business_definition = 'Internal Reports must have use an entity it does not generate'
		self.rule_authority = 'PROMS-O'
		self.rule_functional_definition = 'Internal report must prov:used a prov:Entity it did not prov:generated '
		self.component_name = 'PROMS Internal Report Class instance'
		self.passed = True
		self.fail_reasons = []
		self.components_total_count = 1
		self.components_failed_count = 0
		self.failed_components = None

		q=report_graph.query(proms_rules.used_entityNotGenerated)
		if not bool(q):
			self.passed = False
			self.fail_reasons.append("The Internal Report does not use and generate different entities.")
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

