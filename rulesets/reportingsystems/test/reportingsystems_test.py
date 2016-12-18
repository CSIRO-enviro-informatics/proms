from rdflib import Graph

from rulesets.reportingsystems import ReportingSytems


def test_reportingsystem_1():
    g = Graph().parse('rs_pass.ttl', format='turtle')
    r = ReportingSytems(g)
    assert r.passed is True


def test_reportingsystem_2():
    g = Graph().parse('rs_fail.ttl', format='turtle')
    r = ReportingSytems(g)
    assert r.passed is False
