import datetime
import json


class Rule:
    """
    Template for a Rule.

    This template class needs to be initialised with the standard Rule required parameters as well as any other
    instance parameters needed for the specific rule operation.

    It returns a standard rule return object which is a Python dict comprised of the Rule object's instance variables.
    """

    def __init__(self, id, name, business_definition, authority, functional_definition, component_name, passed,
                 fail_reasons, components_total_count, components_failed_count, failed_components):
        """
        Initialize the Rule object

        :param id: (string) the ID of the rule, assigned by the project this rule is for
        :param name: (string) the English version of the rule name
        :param business_definition: (string) the business definition of the rule
        :param functional_definition: (string) the functional (pseudocode) definition of the rule
        :param component_name: (string) the name of the component this rule test
        :param instance_parameters: (array of objects) parameters needed by the rule to operate, e.g. sessions, variables etc.
        :return:
        """
        #set the static things
        self.id = id
        self.name = name
        self.business_definition = business_definition
        self.authority = authority
        self.functional_definition = functional_definition
        self.time = datetime.datetime.utcnow()
        self.component_name = component_name

        #set the dynamic things
        self.passed = passed
        self.fail_reasons = fail_reasons
        self.components_total_count = components_total_count
        self.components_failed_count = components_failed_count
        self.failed_components = failed_components
        self.return_object = {
            'id': self.id,
            'name': self.name,
            'business_definition': self.business_definition,
            'authority': self.authority,
            'functional_definition': self.functional_definition,
            'time': self.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'passed': self.passed,
            'fail_reasons': self.fail_reasons,
            'components': {
                'type': self.component_name,
                'count': self.components_total_count,
                'fail_count': self.components_failed_count,
                'failed': self.failed_components
            }
        }

    def get_result(self):
        return self.return_object

    def save_as_json(self, resultset_id, results_dir):
        ruletset_results_filename = 'result_ruleset_' + resultset_id + '_rule_' + self.id + '_' + self.time.strftime('%Y-%m-%dT%H-%M-%SZ') + '.json'
        with open(results_dir + ruletset_results_filename, 'w') as outfile:
            json.dump(self.return_object, outfile, indent=4)

        return ruletset_results_filename