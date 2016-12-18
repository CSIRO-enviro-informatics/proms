from rulesets import RuleSet, Rule
from proms_report import PromsReport


class ExternalReport(RuleSet):
    def __init__(self, g):
        # only run second Rule if first passes
        rules = []
        r1 = HasIdenticalActivities(g)
        rules.append(r1)
        if r1.passed:
            r2 = HasUsedAndGeneratedEntities(g)
            rules.append(r2)
        RuleSet.__init__(
            self,
            'PROMS External Report',
            rules,
            [PromsReport(g)])  # dependent on PromsReport


class HasIdenticalActivities(Rule):
    def __init__(self, g):
        self.passed = True
        self.fail_reasons = []

        qres = g.query('''
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            ASK
            WHERE {
                ?s a proms:ExternalReport .
                ?s proms:startingActivity ?sa .
                ?s proms:endingActivity ?sa .
            }
            ''')
        if not bool(qres):
            self.fail_reasons.append('The Report does not contain a single Activity indicated as both the starting and ending Activity')

        # determine passed due to any fail_reasons
        # if there are any failure reasons it means it's failed
        if self.fail_reasons:
            self.passed = False

        Rule.__init__(
            self,
            'Single Activity',
            'The Report has the same starting & ending Activity',
            'PROMS Ontology',
            self.passed,
            self.fail_reasons,
            1,  # the number of individual test
            len(self.fail_reasons)  # the number of test failed
        )


class HasUsedAndGeneratedEntities(Rule):
    def __init__(self, g):
        self.passed = True
        self.fail_reasons = []

        qres = g.query('''
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            ASK
            WHERE {
                ?s a proms:ExternalReport .
                ?s proms:startingActivity ?act .
                ?act prov:used ?e1.
                ?e1 a prov:Entity.
            }
            ''')
        if not bool(qres):
            self.fail_reasons.append('The Report\'s Activity does not use any Entities')

        qres = g.query('''
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            ASK
            WHERE {
                ?s a proms:ExternalReport .
                ?s proms:startingActivity ?act .
                ?act prov:generated ?e1.
                ?e1 a prov:Entity.
            }
            ''')
        if not bool(qres):
            self.fail_reasons.append('The Report\'s Activity does not generate any Entities')

        # determine passed due to any fail_reasons
        # if there are any failure reasons it means it's failed
        if self.fail_reasons:
            self.passed = False

        Rule.__init__(
            self,
            'Activity Entities',
            'The report\'s Activity has at least one prov:used and one prov:generated Entity',
            'PROMS Ontology',
            self.passed,
            self.fail_reasons,
            2,  # the number of individual test
            len(self.fail_reasons)  # the number of test failed
        )
