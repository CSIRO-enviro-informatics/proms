__author__ = 'ayr016'
from ruleset import RuleSet


class StackedRuleSet(RuleSet):
	"""
	Chaining of rulesets.  Note that passing the current ruleset does not guarantee that all the
	dependencies were passed too
	"""
	def __init__(self,id, name, owner, rules_results, passed, dependencies):
		"""
		Extends Ruleset by having a list of dependencies
		:param id:
		:param name:
		:param owner:
		:param rules_results:
		:param passed:
		:param dependencies:
		:return:
		"""
		assert isinstance(dependencies, list)

		RuleSet.__init__(self, id, name, owner, rules_results, passed)

		self.dependencies = dependencies

		self.return_object = []
		self.return_object.append({
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'time': self.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'passed': self.passed,
            'rule_results': self.rules_results,
        })

		for d in self.dependencies:
			assert isinstance(d, dict), "stacked ruleset dependencies should be evaluated and get_result appended to self.dependencies"
			self.return_object.append(d)


