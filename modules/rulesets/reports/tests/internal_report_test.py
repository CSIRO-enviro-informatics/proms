from rdflib import Graph

from modules.rulesets.reports import InternalReport


def test_internalreport_1():
    g = Graph().parse('internal_report_pass.ttl', format='turtle')
    r = InternalReport(g)
    assert r.passed is True


def test_internalreport_2():
    g = Graph().parse('internal_report_fail.ttl', format='turtle')
    r = InternalReport(g)
    assert r.passed is False


def test_internalreport_3():
    g = Graph().parse('internal_report_fail2.ttl', format='turtle')
    r = InternalReport(g)
    assert r.passed is False


if __name__ == '__main__':
    test_internalreport_1()
    test_internalreport_2()
    test_internalreport_3()
