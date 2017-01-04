from rdflib import Graph
from report import ExternalReport


def test_externalreport_1():
    g = Graph().parse('external_report_pass.ttl', format='turtle')
    r = ExternalReport(g)
    assert r.passed is True


def test_externalreport_2():
    g = Graph().parse('external_report_fail.ttl', format='turtle')
    r = ExternalReport(g)
    assert r.passed is False


if __name__ == '__main__':
    test_externalreport_1()
    test_externalreport_2()
