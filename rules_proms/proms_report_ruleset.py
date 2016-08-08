from rules_templates import RuleSet, Rule
import proms_rules as proms_rules


class PromsReportValid(RuleSet):
	"""
	test http://promsns.org/def/proms#Report
	The key result here is that there must be a super-class of Basic/Internal/External
	"""

	def __init__(self, graph):
		ruleset_id = 'old_fashioned_proms_report'
		ruleset_name = 'PROMS Report'
		rules_results = []

		rules_results.append(HasReport(graph).get_result())
		# note everything else in proms_report belongs in a higher ruleset

		passed = True
		# all rules must have passed for the ruleset to have passed
		for rules_result in rules_results:
			if not rules_result['passed']:
				passed = False
				break

		#
		#   Call the base RuleSet constructor
		#
		RuleSet.__init__(self,
						 ruleset_id,
						 ruleset_name,
						 'Nicholas Car (nicholas.car@csiro.au)',
						 rules_results,
						 passed)


class HasReport(Rule):
	"""
	Checks a graph has a valid report class
	"""

	def __init__(self, report_graph):
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

		q=report_graph.query(proms_rules.has_report)

		if not bool(q):
			self.passed = False
			self.fail_reasons.append('The Report class does not contain a dc:title')

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