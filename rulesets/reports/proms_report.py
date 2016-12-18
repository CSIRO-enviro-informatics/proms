from rulesets import RuleSet, Rule
from prov_constraints import ProvConstraints


class PromsReport(RuleSet):
    """
    Rules mandated by the PROMS Ontology
    """
    def __init__(self, g):
        RuleSet.__init__(
            self,
            'PROMS Report',
            [ReportProperties(g), HasStartingAndEndingActivities(g)],
            [ProvConstraints(g)]
        )


class ReportProperties(Rule):
    def __init__(self, g):
        self.passed = True
        self.fail_reasons = []

        # has a Report class
        qres = g.query('''
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?s
        WHERE {
            { ?s  a            proms:Report .}
            UNION
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
        }
        ''')
        if not bool(qres):
            self.fail_reasons.append('The report does not contain a Report class or subclass')

        # has a label
        qres = g.query('''
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?s
        WHERE {
            { ?s  a            proms:Report .}
            UNION
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  rdfs:label     ?t .
        }
        ''')
        if not bool(qres):
            self.fail_reasons.append('The Report class does not contain an rdfs:label')

        # has a nativeId
        qres = g.query('''
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?s
        WHERE {
            { ?s  a            proms:Report .}
            UNION
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  proms:nativeId  ?j .
        }
        ''')
        if not bool(qres):
            self.fail_reasons.append('The Report class does not contain a proms:nativeId')

        # has a ReportingSystem
        qres = g.query('''
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?s
        WHERE {
            { ?s  a            proms:Report .}
            UNION
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  proms:reportingSystem  ?rs .
        }
        ''')
        if not bool(qres):
            self.fail_reasons.append('The Report class does not contain a proms:reportingSystem')

        # has a generatedAtTime
        qres = g.query('''
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        ASK
        WHERE {
            { ?s  a            proms:Report .}
            UNION
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s prov:generatedAtTime ?t .
        }
        ''')
        if not bool(qres):
            self.fail_reasons.append('The Report class does not contain a prov:generatedAtTime value')

        # determine passed due to any fail_reasons
        # if there are any failure reasons it means it's failed
        if self.fail_reasons:
            self.passed = False

        Rule.__init__(
            self,
            'Report Class properties',
            'Reports Class objects must contain certain properties set out in the PROMS Ontology',
            'PROMS Ontology',
            self.passed,
            self.fail_reasons,
            5,  # the number of individual test
            len(self.fail_reasons)  # the number of test failed
        )


class HasStartingAndEndingActivities(Rule):
    def __init__(self, g):
        self.passed = True
        self.fail_reasons = []

        qres = g.query('''
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            ASK
            WHERE {
                { ?s  a            proms:Report .}
                UNION
                { ?s  a            proms:BasicReport .}
                UNION
                { ?s  a            proms:ExternalReport .}
                UNION
                { ?s  a            proms:InternalReport .}
                ?s  proms:startingActivity  ?rs .
                ?rs a prov:Activity .
            }
        ''')
        if not bool(qres):
            self.fail_reasons.append('The Report class does not contain a proms:startingActivity')

        qres = g.query('''
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            ASK
            WHERE {
                { ?s  a            proms:Report .}
                UNION
                { ?s  a            proms:BasicReport .}
                UNION
                { ?s  a            proms:ExternalReport .}
                UNION
                { ?s  a            proms:InternalReport .}
                ?s  proms:endingActivity  ?rs .
                ?rs a prov:Activity .
            }
        ''')
        if not bool(qres):
            self.fail_reasons.append('The Report class does not contain a proms:endingActivity')

        # determine passed due to any fail_reasons
        # if there are any failure reasons it means it's failed
        if self.fail_reasons:
            self.passed = False

        Rule.__init__(
            self,
            'Start End Activities',
            'The report has starting & ending Activities',
            'PROMS Ontology',
            self.passed,
            self.fail_reasons,
            2,  # the number of individual test
            len(self.fail_reasons)  # the number of test failed
        )


# TODO: Rule Activity properties (start & end time only)


# TODO: Rule Report/Activity relations (report cannot have been generated before activity)

