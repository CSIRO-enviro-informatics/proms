import datetime


class Rule:
    """
    Template for a Rule.

    This template class needs to be initialised with the standard Rule required parameters as well as any other
    instance parameters needed for the specific rule operation.

    It returns a standard rule return object which is a Python dict comprised of the Rule object's instance variables.
    """

    def __init__(self,
                 name,
                 definition,
                 authority,
                 passed,
                 fail_reasons,
                 components_total_count,
                 components_failed_count,
                 # components_failed -- night add this later
                 ):
        """
        Initialize the Rule object

        :param id: (string) the ID of the rule, assigned by the project this rule is for
        :param name: (string) the English version of the rule name
        :param definition: (string) the definition of the rule in words
        :param authority: (string) where the rule comes from
        :param passed (boolean)
        :param fail_reasons (list) a list of all the reasons the rule failed
        :param components_total_count (int) the number of things that could have failed
        :param components_failed_count (int) the number of things that did fail
        :return:
        """
        # set the static things
        self.id = Rule.make_id(name)
        self.name = name
        self.definition = definition
        self.authority = authority
        self.time = datetime.datetime.now()

        # set the dynamic things
        self.passed = passed
        self.fail_reasons = fail_reasons
        self.components_total_count = components_total_count
        self.components_failed_count = components_failed_count
        #self.components_failed = components_failed

    @staticmethod
    def make_id(name):
        # replace all nonASCII characters
        id = ''.join([i if ord(i) < 128 else '' for i in name])
        # replace spaces with underscores
        id = id.replace(' ', '_')
        id = id.lower()
        return id