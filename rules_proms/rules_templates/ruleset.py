import datetime
import json


class RuleSet:
    """
    Template for a RuleSet

    This template class needs to be initialised with the standard RuleSet required parameters as well as any other
    instance parameters needed for the specific Rule class instances that it contains to operate.

    It returns a standard ruleset return object which is a Python dict comprised of the RuleSet object's instance
    variables.
    """

    def __init__(self, id, name, owner, rules_results, passed):
        """
        Initialise the RuleSet

        :param id: (string) ID of the RuleSet, allocated by the project
        :param name: (string) name of the RuleSet
        :param owner: (URI) URI of the owner of the RuleSet
        :return: (dict) ruleset return object
        """
        self.id = id
        self.name = name
        self.owner = owner
        self.time = datetime.datetime.utcnow()
        self.passed = passed
        self.rules_results = rules_results
        self.return_object = {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'time': self.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'passed': self.passed,
            'rule_results': self.rules_results,
        }

    def get_result(self):
        """

        :rtype : dict of rules
        """
        return self.return_object

    def save_as_json(self, results_dir):
        ruleset_results_filename = 'results_ruleset_' + self.id + '_' + self.time.strftime('%Y-%m-%dT%H-%M-%SZ') + '.json'
        with open(results_dir + ruleset_results_filename, 'w') as outfile:
            json.dump(self.return_object, outfile, indent=4)

        return ruleset_results_filename