from rules_templates import RuleSet, Rule
import prov_constraints_functions as provconstraints


class ProvConstraints(RuleSet):
	"""
    Rules derived from PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints) using
    Paul Groth's provcheck SPARQL queries (https://github.com/pgroth/prov-check)
    """

	def __init__(self, prov_graph):
		ruleset_id = 'provconstraints'
		ruleset_name = 'PROV Constraints'
		rules_results = []

		#
		# Rule code
		#
		#run each group of constraint tests, equivalent to validate(g)
		rules_results.append(Cycle(prov_graph).get_result())

		rules_results.append(Impossibility(prov_graph).get_result())

		rules_results.append(KeyConstraints(prov_graph).get_result())
		#
		rules_results.append(TypeConstraints(prov_graph).get_result())
		#
		rules_results.append(Uniqueness(prov_graph).get_result())

		passed = False
		# all rules must have passed for the ruleset to have passed
		for rules_result in rules_results:
			if not rules_result['passed']:
				passed = False
				break

		#
		#   Call the base RuleSet constructor
		#
		RuleSet.__init__(self,
						 ruleset_id,
						 ruleset_name,
						 'Nicholas Car (nicholas.car@csiro.au)',
						 rules_results,
						 passed)


# TODO: fix inability to use SPARQL 1.1 paths in query
class Cycle(Rule):
	"""
    This class wraps provconstraints.checkCycle() with a Rule return
    """

	def __init__(self, prov_graph):
		#
		#   Rule details
		#
		rule_id = 'cycle'
		rule_name = 'PROV Cycle constraints'
		rule_business_definition = 'Constraints '
		rule_authority = 'PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints)'
		rule_functional_definition = '''

        '''

		#
		#   Rule reporting vars
		#
		failreason = None
		fail_reasons = []
		components_total_count = 1
		components_failed_count = 0
		failed_components = None

		#
		#   Rule code
		#
		#
		failreason = provconstraints.checkCycle(prov_graph)
		if failreason is not None:
			components_failed_count = 1
			fail_reasons.append("Cycle constraints failed: " + str(failreason))

		#
		#   Call the base Rule constructor
		#
		Rule.__init__(self,
					  rule_id,
					  rule_name,
					  rule_business_definition,
					  rule_authority,
					  rule_functional_definition,
					  'Nicholas Car (nicholas.car@csiro.au)',
					  failreason is None,
					  fail_reasons,
					  components_total_count,
					  components_failed_count,
					  failed_components)


#TODO: fix inability to use SPARQL 1.1 paths in query
class Impossibility(Rule):
	"""
    This class wraps provconstraints.checkImpossibility() with a Rule return
    """

	def __init__(self, prov_graph):
		#
		#   Rule details
		#
		rule_id = 'impossibility'
		rule_name = 'PROV Impossibility constraints'
		rule_business_definition = 'Constraints '
		rule_authority = 'PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints)'
		rule_functional_definition = '''

        '''

		#
		#   Rule reporting vars
		#
		failreason = None
		fail_reasons = []
		components_total_count = 1
		components_failed_count = 0
		failed_components = None

		#
		#   Rule code
		#
		#
		failreason = provconstraints.checkImpossibility(prov_graph)
		if failreason is not None:
			components_failed_count = 1
			fail_reasons.append("Impossibility constraints failed: " + str(failreason))

		#
		#   Call the base Rule constructor
		#
		Rule.__init__(self,
					  rule_id,
					  rule_name,
					  rule_business_definition,
					  rule_authority,
					  rule_functional_definition,
					  'Nicholas Car (nicholas.car@csiro.au)',
					  failreason is None,
					  fail_reasons,
					  components_total_count,
					  components_failed_count,
					  failed_components)


class KeyConstraints(Rule):
	"""
    This class wraps provconstraints.checkKeyConstraints() with a Rule return
    """

	def __init__(self, prov_graph):
		#
		#   Rule details
		#
		rule_id = 'keyConstraints'
		rule_name = 'PROV KeyConstraints constraints'
		rule_business_definition = 'Constraints '
		rule_authority = 'PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints)'  # this spelling mistake is required
		rule_functional_definition = '''

        '''

		#
		#   Rule reporting vars
		#
		failreason = None
		fail_reasons = []
		components_total_count = 1
		components_failed_count = 0
		failed_components = None

		#
		#   Rule code
		#
		#
		failreason = provconstraints.checkKeyConstraints(prov_graph)
		if failreason is not None:
			components_failed_count = 1
			fail_reasons.append("KeyConstraints constraints failed: " + str(failreason))

		#
		#   Call the base Rule constructor
		#
		Rule.__init__(self,
					  rule_id,
					  rule_name,
					  rule_business_definition,
					  rule_authority,
					  rule_functional_definition,
					  'Nicholas Car (nicholas.car@csiro.au)',
					  failreason is None,
					  fail_reasons,
					  components_total_count,
					  components_failed_count,
					  failed_components)


class TypeConstraints(Rule):
	"""
    This class wraps provconstraints.checkKeyConstraints() with a Rule return
    """

	def __init__(self, prov_graph):
		#
		#   Rule details
		#
		rule_id = 'typeConstraints'
		rule_name = 'PROV TypeConstraints constraints'
		rule_business_definition = 'Constraints '
		rule_authority = 'PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints)'
		rule_functional_definition = '''

        '''

		#
		#   Rule reporting vars
		#
		failreason = None
		fail_reasons = []
		components_total_count = 1
		components_failed_count = 0
		failed_components = None

		#
		#   Rule code
		#
		#
		failreason = provconstraints.checkTypeConstraints(prov_graph)
		if failreason is not None:
			components_failed_count = 1
			fail_reasons.append("TypeConstraints constraints failed: " + str(failreason))

		#
		#   Call the base Rule constructor
		#
		Rule.__init__(self,
					  rule_id,
					  rule_name,
					  rule_business_definition,
					  rule_authority,
					  rule_functional_definition,
					  'Nicholas Car (nicholas.car@csiro.au)',
					  failreason is None,
					  fail_reasons,
					  components_total_count,
					  components_failed_count,
					  failed_components)


class Uniqueness(Rule):
	"""
    This class wraps provconstraints.checkUniqueness() with a Rule return
    """

	def __init__(self, prov_graph):
		#
		#   Rule details
		#
		rule_id = 'uniqueness'
		rule_name = 'PROV Uniqueness constraints'
		rule_business_definition = 'Constraints '
		rule_authority = 'PROV Constraints (http://www.w3.org/TR/prov-implementations/#prov-contraints)'
		rule_functional_definition = '''

        '''

		#
		#   Rule reporting vars
		#
		failreason = None
		fail_reasons = []
		components_total_count = 1
		components_failed_count = 0
		failed_components = None

		#
		#   Rule code
		#
		#
		failreason = provconstraints.checkUniqueness(prov_graph)
		if failreason is not None:
			components_failed_count = 1
			fail_reasons.append("Uniqueness constraints failed: " + str(failreason))

		#
		#   Call the base Rule constructor
		#
		Rule.__init__(self,
					  rule_id,
					  rule_name,
					  rule_business_definition,
					  rule_authority,
					  rule_functional_definition,
					  'Nicholas Car (nicholas.car@csiro.au)',
					  failreason is None,
					  fail_reasons,
					  components_total_count,
					  components_failed_count,
					  failed_components)