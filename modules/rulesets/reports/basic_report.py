from modules.rulesets import RuleSet
from report import PromsReport


class BasicReport(RuleSet):
    def __init__(self, g):
        RuleSet.__init__(
            self,
            'PROMS Basic Report',
            [],  # that's right, the BasicReport class has no Rules on top of those already in the PROMs Report class!
            [PromsReport(g)])  # it just imports and runs PromsReport
