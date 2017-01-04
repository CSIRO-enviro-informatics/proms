from rdflib import Graph

from modules.rulesets.reports import BasicReport


def test_basicreport_1():
    g = Graph().parse('proms_report_pass.ttl', format='turtle')
    r = BasicReport(g)
    assert r.passed is True


def test_basicreport_2():
    g = Graph().parse('proms_report_fail.ttl', format='turtle')
    r = BasicReport(g)
    assert r.passed is False


if __name__ == '__main__':
    test_basicreport_1()
    test_basicreport_2()

