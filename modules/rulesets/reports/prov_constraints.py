from ..ruleset import RuleSet
from ..rule import Rule

from .prov_constraints_functions import *


class ProvConstraints(RuleSet):
    """Rules derived from PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints) using
    Paul Groth's provcheck SPARQL queries (https://github.com/pgroth/prov-check)
    """

    def __init__(self, prov_graph):
        ruleset_name = 'PROV Constraints'
        rules = [
            Cycle(prov_graph),
            Impossibility(prov_graph),
            KeyConstraints(prov_graph),
            TypeConstraints(prov_graph),
            Uniqueness(prov_graph)
        ]

        RuleSet.__init__(self,
                         ruleset_name,
                         rules)


# TODO: fix inability to use SPARQL 1.1 paths in query
class Cycle(Rule):
    """This class wraps provconstraints.checkCycle() with a Rule class
    """

    def __init__(self, g):
        passed = True
        fail_reasons = []
        f = prov_constraints_functions.checkCycle(g)
        if f is not None:
            passed = False
            fail_reasons.append(str(f))  # no need to name the Rule as the Ruleset will append this

        Rule.__init__(self,
                      'PROV Cycle constraints',
                      'Cyclic constraints of the PROV data model',
                      'PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints)',
                      passed,
                      fail_reasons,
                      1,
                      0)


# TODO: fix inability to use SPARQL 1.1 paths in query
class Impossibility(Rule):
    """This class wraps provconstraints.checkImpossibility() with a Rule class
    """

    def __init__(self, g):
        passed = True
        fail_reasons = []
        f = prov_constraints_functions.checkImpossibility(g)
        if f is not None:
            passed = False
            fail_reasons.append(str(f))  # no need to name the Rule as the Ruleset will append this

        Rule.__init__(self,
                      'PROV Impossibility constraints',
                      'Impossibility constraints of the PROV data model',
                      'PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints)',
                      passed,
                      fail_reasons,
                      1,
                      0)


class KeyConstraints(Rule):
    """This class wraps provconstraints.checkKeyConstraints() with a Rule class
    """

    def __init__(self, g):
        passed = True
        fail_reasons = []
        f = prov_constraints_functions.checkKeyConstraints(g)
        if f is not None:
            passed = False
            fail_reasons.append(str(f))  # no need to name the Rule as the Ruleset will append this

        Rule.__init__(self,
                      'PROV Key Constraints',
                      'Key Constraints of the PROV data model',
                      'PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints)',
                      passed,
                      fail_reasons,
                      1,
                      0)


class TypeConstraints(Rule):
    """This class wraps provconstraints.checkTypeConstraints() with a Rule class
    """

    def __init__(self, g):
        passed = True
        fail_reasons = []
        f = prov_constraints_functions.checkTypeConstraints(g)
        if f is not None:
            passed = False
            fail_reasons.append(str(f))  # no need to name the Rule as the Ruleset will append this

        Rule.__init__(self,
                      'PROV Type Constraints',
                      'Type Constraints of the PROV data model',
                      'PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints)',
                      passed,
                      fail_reasons,
                      1,
                      0)


class Uniqueness(Rule):
    """This class wraps provconstraints.checkUniqueness() with a Rule class
    """

    def __init__(self, g):
        passed = True
        fail_reasons = []
        f = prov_constraints_functions.checkUniqueness(g)
        if f is not None:
            passed = False
            fail_reasons.append(str(f))  # no need to name the Rule as the Ruleset will append this

        Rule.__init__(self,
                      'PROV Uniqueness Constraints',
                      'Uniqueness Constraints of the PROV data model',
                      'PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints)',
                      passed,
                      fail_reasons,
                      1,
                      0)