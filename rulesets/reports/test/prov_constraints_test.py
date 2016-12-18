from rdflib import Graph

from rulesets.reports import ProvConstraints


def test_provconstraints_1():
    g = Graph().parse('prov_constraints_pass.ttl', format='turtle')
    r = ProvConstraints(g)
    assert r.passed is True


def test_provconstraints_2():
    g = Graph().parse('prov_constraints_fail.ttl', format='turtle')
    r = ProvConstraints(g)
    assert r.passed is False


if __name__ == '__main__':
    test_provconstraints_1()
    test_provconstraints_2()