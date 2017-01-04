from rdflib import Graph

from modules.rulesets import PromsReport


def test_promsreport_1():
    g = Graph().parse('proms_report_pass.ttl', format='turtle')
    r = PromsReport(g)
    assert r.passed is True


def test_promsreport_2():
    g = Graph().parse('proms_report_fail.ttl', format='turtle')
    r = PromsReport(g)
    assert r.passed is False


if __name__ == '__main__':
    test_promsreport_1()
    test_promsreport_2()

