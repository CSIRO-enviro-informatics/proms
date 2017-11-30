import datetime
from .rule import Rule


class RuleSet:
    """
    Template for a RuleSet

    This template class needs to be initialised with the standard RuleSet required parameters as well as any other
    instance parameters needed for the specific Rule class instances that it contains to operate.

    It returns a standard ruleset return object which is a Python dict comprised of the RuleSet object's instance
    variables.
    """

    def __init__(self, name, rules, dependencies=None):
        """
        Initialise the RuleSet

        :param id: (string) ID of the RuleSet, allocated by the project
        :param name: (string) name of the RuleSet
        :return: (dict) ruleset return object
        """

        self.id = RuleSet.make_id(name)
        self.name = name
        self.time = datetime.datetime.now()
        self.passed = True  # if any of the Rules fail, so too does the RuleSet
        self.rules = rules
        self.fail_reasons = []
        for r in rules:
            assert isinstance(r, Rule), 'RuleSets\' rules must be Rules'
            if not r.passed:
                self.passed = False
                for fr in r.fail_reasons:
                    self.fail_reasons.append('Rule %s: %s' % (r.name, fr))

        # dependencies
        if dependencies is not None:
            assert isinstance(dependencies, list)
            for d in dependencies:
                assert isinstance(d, RuleSet), 'RuleSets\' dependencies must be other RuleSets'
            self.dependencies = dependencies

            # evaluate adherence to the dependencies
            for d in self.dependencies:
                if not d.passed:
                    self.passed = False

                    for fr in d.fail_reasons:
                        # this will compound the RuleSet name onto the Rule name and the fail reason
                        self.fail_reasons.append('RuleSet %s: %s' % (d.name, fr))

    @staticmethod
    def make_id(name):
        # replace all nonASCII characters
        id = ''.join([i if ord(i) < 128 else '' for i in name])
        # replace spaces with underscores
        id = id.replace(' ', '_')
        id = id.lower()
        return id