from unittest import TestCase
from test_provConstraints import get_graph
from test_provConstraints import format_rule_results

from proms_basic_report_ruleset import PromsBasicReportValid

__author__ = 'ayr016'


class TestPromsBasicReportValid(TestCase):
	def test_simple_pass(self):
		# filename = ".//test//proms_report//test_proms_basic_report_01.ttl"
		filename = ".//test//proms_report//test_proms_report_01.ttl"
		g = get_graph(filename)
		pr = PromsBasicReportValid(g)
		r = pr.get_result()

		for ruleset in r:
			# print ruleset
			for rule in ruleset['rule_results']:
				if not rule['passed']:
					self.fail("Results should be valid: {0}"
								  .format(format_rule_results(rule_result_set=r)))


					# todo: run this and keep debugging.  It's making a valid http request, but the request is failing for 401





