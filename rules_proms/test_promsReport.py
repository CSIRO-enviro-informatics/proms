from unittest import TestCase
from proms_report import PromsReport
from test_provConstraints import format_rule_results
from test_provConstraints import get_graph

__author__ = 'ayr016'


class TestPromsReport(TestCase):
    def test_simple_pass(self):
        filename = ".//test//proms_report//test_proms_report_01.ttl"
        g = get_graph(filename)
        pr = PromsReport(g)
        r = pr.get_result()
        for rule in r['rule_results']:
            if not rule['passed']:
                self.fail("Results should be valid: {0}"
                              .format(format_rule_results(rule_result_set=r)))

    def test_simple_fail(self):
        """
        Expected result is "The Report class does not contain a proms:nativeId"
        :return:
        """
        filename = ".//test//proms_report//test_proms_report_02.ttl"
        g = get_graph(filename)
        pr = PromsReport(g)
        r = pr.get_result()
        for rule in r['rule_results']:
            if not rule['passed']:
                for msg in rule['fail_reasons']:
                    if not msg == "The Report class does not contain a proms:nativeId":
                        self.fail("report is supposed to fail on proms:nativeId and does not.")

    def test_simple_pass_with_prov(self):
        from prov_constraints import ProvConstraints
        filename = ".//test//proms_report//test_proms_report_01.ttl"
        g = get_graph(filename)
        pr = PromsReport(g)
        r = pr.get_result()
        for rule in r['rule_results']:
            if not rule['passed']:
                self.fail("Results should be valid: {0}"
                              .format(format_rule_results(rule_result_set=r)))

        pv = ProvConstraints(g)
        r = pv.get_result()
        for rule in r['rule_results']:
            if not rule['passed']:
                self.fail("Results should be valid: {0}"
                              .format(format_rule_results(rule_result_set=r)))

    def test_simple_fail_prov(self):
        """This is supposed to pass prov"""
        from prov_constraints import ProvConstraints
        filename = ".//test//proms_report//test_proms_report_02.ttl"
        g = get_graph(filename)
        pv = ProvConstraints(g)
        r = pv.get_result()
        for rule in r['rule_results']:
            if not rule['passed']:
                self.fail("Results should be valid: {0}"
                              .format(format_rule_results(rule_result_set=r)))