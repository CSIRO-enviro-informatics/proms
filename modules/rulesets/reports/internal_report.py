from modules.rulesets import RuleSet, Rule
from .report import PromsReport


class InternalReport(RuleSet):
    def __init__(self, g):
        # only run second Rule if first passes
        rules = []
        # TODO: check it's actually an Internal report
        r1 = HasDifferentActivities(g)
        rules.append(r1)
        if r1.passed:
            r2 = StartBeforeEnd(g)
            rules.append(r2)
        RuleSet.__init__(
            self,
            'PROMS External Report',
            rules,
            [PromsReport(g)])  # dependent on PromsReport


class HasDifferentActivities(Rule):
    def __init__(self, g):
        self.passed = True
        self.fail_reasons = []

        q = g.query('''
            PREFIX proms: <http://promsns.org/def/proms#>
            ASK
            WHERE {
                ?s a proms:InternalReport .
                ?s proms:startingActivity ?sa .
                ?s proms:endingActivity ?ea .
                FILTER (?sa != ?ea)
            }
            ''')

        if not bool(q):
            self.fail_reasons.append(
                'The Report does not contain at least two different Activities '
                'indicated by the starting and ending Activity')

        # determine passed due to any fail_reasons
        # if there are any failure reasons it means it's failed
        if self.fail_reasons:
            self.passed = False

        Rule.__init__(
            self,
            'Single Activity',
            'The Report has the different starting & ending Activities',
            'PROMS Ontology',
            self.passed,
            self.fail_reasons,
            1,  # the number of individual tests
            len(self.fail_reasons)  # the number of tests failed
        )


class StartBeforeEnd(Rule):
    def __init__(self, g):
        self.passed = True
        self.fail_reasons = []

        q = g.query('''
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX proms: <http://promsns.org/def/proms#>
            ASK
            WHERE {
                ?s a proms:InternalReport .
                ?s proms:startingActivity ?sa .
                ?sa prov:startedAtTime ?sasat .
                ?s proms:endingActivity ?ea .
                ?ea prov:startedAtTime ?easat .
                FILTER (?sasat < ?easat)
            }
            ''')

        if not bool(q):
            self.fail_reasons.append(
                'The Report\'s starting Activity doesn\'t start before its ending Activity starts')

        # determine passed due to any fail_reasons
        # if there are any failure reasons it means it's failed
        if self.fail_reasons:
            self.passed = False

        Rule.__init__(
            self,
            'Starting Ending Activity',
            'The starting Activity of the Report must start before the Ending Activity starts',
            'PROMS Ontology',
            self.passed,
            self.fail_reasons,
            1,  # the number of individual tests
            len(self.fail_reasons)  # the number of tests failed
        )

# TODO: Rule must have 1+ used Entity

# TODO: Rule must have 1+ generated Entity

