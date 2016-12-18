from rulesets import RuleSet, Rule
from ..reports.prov_constraints import ProvConstraints
import rdflib
import StringIO


class PromsPingback(RuleSet):
    def __init__(self, request, pingback_endpoint):
        if request.headers.get('Content-Type') == 'text/ntriples':
            format = 'n3'
        elif request.headers.get('Content-Type') == 'text/n3':
            format = 'n3'
        elif request.headers.get('Content-Type') == 'application/rdf+xml':
            format = 'xml'
        elif request.headers.get('Content-Type') == 'application/ld+json':
            format = 'json-ld'
        else:  # 'text/turtle'
            format = 'turtle'

        g = rdflib.Graph().parse(StringIO.StringIO(request.content), format=format)

        rules = []
        # r1, as per http://promsns.org/pingbacks/validator/about, is PROV-O compliance
        r0 = Header(request)
        rules.append(r0)
        if r0.passed:
            r2 = PingbackDeclaration(g, pingback_endpoint)
            rules.append(r2)
            if r2.passed:
                r3 = EntitiesUsed(g)
                rules.append(r3)

        RuleSet.__init__(
            self,
            'PROMS Pingback message',
            rules,
            [ProvConstraints(g)])  # dependent on PromsReport


class Header(Rule):
    def __init__(self, request):
        self.passed = True
        self.fail_reasons = []

        # must be an RDF content type
        rdf_content_types = [
            'text/turtle',
            'text/ntriples',
            'text/n3',
            'application/rdf+xml',
            'application/ld+json'
        ]
        if request.headers.get('Content-Type') not in rdf_content_types:
            self.passed = False
            self.fail_reasons.append(
                'PROMS pingback messages must have an RDF Content-Type')

        Rule.__init__(
            self,
            'PROMS pingback header',
            'The pingback must have a valid PROMS-specified header',
            'PROVMS-O Pingbacks',
            self.passed,
            self.fail_reasons,
            1,  # the number of individual test
            len(self.fail_reasons)  # the number of test failed
        )


class PingbackDeclaration(Rule):
    def __init__(self, g, pingback_endpoint):
        self.passed = True
        self.fail_reasons = []
        q = '''
            PREFIX prov: <http://www.w3.org/ns/prov#>
            ASK
            WHERE {
                {?e  a prov:Entity .}
                UNION
                {?e  a prov:Plan .}
                ?e    prov:pingback <%s> .
            }
        ''' % (pingback_endpoint)
        qres = g.query(q)
        if not bool(qres):
            self.passed = False
            self.fail_reasons.append('R2: No prov:Entity contains a prov:pingback property pointing to {}'.format(pingback_endpoint))

        Rule.__init__(
            self,
            'Pingback Declaration',
            'At least one prov:Entity (or subclass) must declare a prov:pingback property with the pingback target URI as its range value (object).',
            'PROV-AQ',
            self.passed,
            self.fail_reasons,
            1,  # the number of individual test
            len(self.fail_reasons)  # the number of test failed
        )


class EntitiesUsed(Rule):
    def __init__(self, g):
        self.passed = True
        self.fail_reasons = []

        # to get to this rule, the PingbackDeclaration Rule must already have passed which means that there is at least
        # one Entity which has a prov:pingback property
        q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        ASK
        WHERE {
            ?e prov:pingback ?pb .
            {?a prov:generated ?e . }
            UNION
            {?e prov:wasGeneratedBy ?a . }
        }
        '''
        qres = g.query(q)
        if bool(qres):
            self.passed = False
            self.fail_reasons.append(
                'R3: Pingbacks cannot be sent for Entities declared as prov:wasGeneratedBy or prov:wasDerivedFrom in the pingbacked graph')

        Rule.__init__(
            self,
            'Pingback Declaration',
            'Entities being pingbacked for must be prov:used in the pingback graph',
            'PROV-AQ',
            self.passed,
            self.fail_reasons,
            1,  # the number of individual test
            len(self.fail_reasons)  # the number of test failed
        )