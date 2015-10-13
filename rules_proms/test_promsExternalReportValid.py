__author__ = 'ayr016'
from unittest import TestCase
from test_provConstraints import get_graph
from test_provConstraints import format_rule_results

from proms_external_report_ruleset import PromsExternalReportValid


class TestExternalReportValid(TestCase):
	def test_simple_pass(self):
		# filename = ".//test//proms_report//test_proms_basic_report_01.ttl"
		filename = ".//test//proms_report/test_proms_external_report_pass_01.ttl"
		g = get_graph(filename)
		pr = PromsExternalReportValid(g)
		r = pr.get_result()

		for ruleset in r:
			print ruleset
			for rule in ruleset['rule_results']:
				if not rule['passed']:
					self.fail("Results should be valid: {0}"
								  .format(format_rule_results(rule_result_set=r)))

	def test_simple_fail_generation(self):
		filename = ".//test//proms_report/test_proms_external_report_fail_generation.ttl"
		g = get_graph(filename)
		pr = PromsExternalReportValid(g)
		r = pr.get_result()

		for ruleset in r:
			print ruleset
			for rule in ruleset['rule_results']:
				if rule['id'] == 'ExternalReportUsedAndGeneratedEntities':
					if rule['passed']:
						self.fail('Should fail validation - no entity generated')
				elif not rule['passed']:
					self.fail("Results except generation should be valid: {0}"
								  .format(format_rule_results(rule_result_set=r)))


	def test_simple_fail(self):
		# filename = ".//test//proms_report//test_proms_basic_report_01.ttl"
		filename = ".//test//proms_report//test_proms_report_01.ttl"
		g = get_graph(filename)
		pr = PromsExternalReportValid(g)
		r = pr.get_result()

		for ruleset in r:
			print ruleset
			for rule in ruleset['rule_results']:
				if rule['id'] == 'ExternalReportHasIdenticalActivities':
					if rule['passed']:
						self.fail('starting and ending activities are not identical, this should fail')
				elif not rule['passed']:
					self.fail("Results should be valid: {0}"
								  .format(format_rule_results(rule_result_set=r)))
