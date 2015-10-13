from unittest import TestCase
from test_provConstraints import get_graph
from test_provConstraints import format_rule_results

from proms_report_ruleset import PromsReportValid

__author__ = 'ayr016'


class TestPromsReportValid(TestCase):
	def test_simple_pass(self):
		filename = ".//test//proms_report//test_proms_report_01.ttl"
		g = get_graph(filename)
		pr = PromsReportValid(g)
		r = pr.get_result()
		for rule in r['rule_results']:
			if not rule['passed']:
				self.fail("Results should be valid: {0}"
							  .format(format_rule_results(rule_result_set=r)))