import unittest
from unittest import TestCase
from prov_constraints import ProvConstraints
import os
import sys

__author__ = 'ayr016'


def get_graph(file_or_uri, format="n3"):
	import rdflib

	g = rdflib.Graph()
	g.parse(file_or_uri, format=format)

	return g


def format_rule_results(rule_result_set, print_=False):
	"""if any rule fails, the ruleset failed.  However, that could mean
	that the test passed."""
	result_string = ""
	if isinstance(rule_result_set, dict):
		for rule in rule_result_set['rule_results']:
			if rule['passed']:
				result_string = "".join((result_string, '\nPassed ', rule['id']))
			else:
				result_string = "".join((result_string, '\nFailed: '))
				for msg in rule['fail_reasons']:
					result_string = "".join((result_string, '\n', msg))
		if print_:
			print result_string
		return result_string
	else:
		for rule_result in rule_result_set:
			for rule in rule_result['rule_results']:
				if rule['passed']:
					result_string = "".join((result_string, '\nPassed ', rule['id']))
				else:
					result_string = "".join((result_string, '\nFailed: '))
					for msg in rule['fail_reasons']:
						result_string = "".join((result_string, '\n', msg))
			if print_:
				print result_string
			return result_string
def get_prov_constraint_result(source):
	"""
	build and assess the graph of the source against the rules
	:param source: file or url
	:return: results ruleset
	"""
	g = get_graph(source)
	r = ProvConstraints(g).get_result()
	return r



class TestProvConstraints(TestCase):
	def test_valid_prov(self):
		r = get_prov_constraint_result('test/prov_constraints/test_prov_constraints_01.ttl')

		for rule in r['rule_results']:
			if not rule['passed']:
				self.fail("Results should be valid: {0}"
							  .format(format_rule_results(rule_result_set=r)))
				break

	def test_type_attribution_failure(self):
		r = get_prov_constraint_result('test/prov_constraints/test_prov_constraints_02.ttl')

		# There should be exactly one failure, in TypeConstraints
		for rule in r['rule_results']:
			if not rule['passed']:
				if rule['id'] is not "typeConstraints":
					self.fail("Only Type Constraints should fail: {0}"
							  .format(format_rule_results(rule_result_set=r)))
			else:
				if rule['id'] is "typeConstraints":
					self.fail("TypeConstraints should fail: {0}"
							  .format(format_rule_results(rule_result_set=r)))

	def test_uniqueness_failure(self):
		r = get_prov_constraint_result('test/prov_constraints/test_prov_constraints_03.ttl')

		# There should be exactly one failure, in uniqueness
		for rule in r['rule_results']:
			if not rule['passed']:
				if rule['id'] is not "uniqueness":
					self.fail("Only uniqueness should fail: {0}"
							  .format(format_rule_results(rule_result_set=r)))
			else:
				if rule['id'] == "uniqueness":
					self.fail("uniqueness should fail: {0}"
							  .format(format_rule_results(rule_result_set=r)))

	def test_w3set(self):
		"""Run tests from 'https://dvcs.w3.org/hg/prov and check against their expected result.
		Note this takes a very long time (about 20 minutes) to run, and longer in Nose.
		:return:
		"""
		import urllib2
		import re

		testpass=re.compile('.*PASS.*')
		testfail=re.compile('.*FAIL.*')
		key_constraints = re.compile('.*-c2[23].*') # constraints 22-23
		unique = re.compile('.*-c2[4-9].*') # constraints 24-29
		cycle = re.compile('.*-c[34][0-9].*') # constraints 30-49
		type_constraints = re.compile('.*-c50.*') # constraint 50 only
		impossibility = re.compile('.*-c5[1-6].*') # constraints 51-56


		response = urllib2.urlopen('https://dvcs.w3.org/hg/prov/raw-file/default/testcases/rdf-tests.txt')
		html = response.read()
		failreport=[]


		issuecounter = 0

		for line in html.split('\n'):
			if not line.endswith('.ttl'):
				# print 'only testing ttl files'
				continue

			issuecounter += 1

			# tests that are supposed to pass:
			if testpass.match(line):
				# print "{0};".format(line)
				r = get_prov_constraint_result(line)
				for rule in r['rule_results']:
					if not rule['passed']:
						failreport.append((line, format_rule_results(rule_result_set=r)))
						break
				# passreport.append(line)
			# tests that are supposed to fail
			# they must not pass the specified test; don't care about other tests
			elif testfail.match(line):
				r = get_prov_constraint_result(line)
				# supposed to fail for different reasons
				# c25 is supposed to fail on uniqueness
				if unique.match(line):
					for rule in r['rule_results']:
						if rule['id'] is "uniqueness" and rule['passed']:
							failreport.append((line, format_rule_results(rule_result_set=r)))
							break
				elif key_constraints.match(line):
					for rule in r['rule_results']:
						if rule['id'] is "keyConstraints" and rule['passed']:
							failreport.append((line, format_rule_results(rule_result_set=r)))
							break
				elif cycle.match(line):
					for rule in r['rule_results']:
						if rule['id'] is "cycle" and rule['passed']:
							failreport.append((line, format_rule_results(rule_result_set=r)))
							break
				elif impossibility.match(line):
					for rule in r['rule_results']:
						if rule['id'] is "impossibility" and rule['passed']:
							failreport.append((line, format_rule_results(rule_result_set=r)))
							break
				elif type_constraints.match(line):
					for rule in r['rule_results']:
						if rule['id'] is "typeConstraints" and rule['passed']:
							failreport.append((line, format_rule_results(rule_result_set=r)))
							break
				# ToDo:
				# prov-o fails are allowed to fail too
		else:
			failreport.append((line, format_rule_results(rule_result_set=r)))

		if len(failreport) is not 0:
			self.fail(str(len(failreport)) + " of " + str(issuecounter) + " tests failed. \n" + str(failreport))



if __name__ == '__main__':
	unittest.main()
