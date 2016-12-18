from rulesets import RuleSet, Rule


class ReportingSytems(RuleSet):
    def __init__(self, graph):
        # only one Rule so far!
        rules = [
            HasLabel(graph)
        ]

        RuleSet.__init__(
            self,
            'PROMS Reporting System',
            rules)


class HasLabel(Rule):
    """Checks to see if the ReportingSystem graph has an rdfs:label string
    """
    def __init__(self, report_graph):
        self.passed = True
        self.fail_reasons = []
        self.components_total_count = 1
        self.components_failed_count = 0

        q = ''' PREFIX proms: <http://promsns.org/def/proms#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                ASK
                WHERE {
                    ?s  a           proms:ReportingSystem .
                    ?s  rdfs:label  ?t .
                }
            '''
        qr = report_graph.query(q)
        if not bool(qr):
            self.passed = False
            self.fail_reasons.append('The Reporting System class does not contain an rdfs:label')

        # Rule constructor
        Rule.__init__(self,
                      'Has a Label',
                      'PROMS-O',
                      'Reporting System must have a label, as defined in the PROMS ontology',
                      self.passed,
                      self.fail_reasons,
                      1,
                      0)
