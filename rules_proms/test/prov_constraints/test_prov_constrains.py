from prov_constraints import ProvConstraints
import urllib2
import re
import datetime
import pydot
import io
import rdf2dot


def get_graph(file_or_uri, format="n3"):
	import rdflib

	g = rdflib.Graph()
	g.parse(file_or_uri, format=format)

	return g


def get_prov_constraint_result(source):
	"""
	build and assess the graph of the source against the rules
	:param source: file or url
	:return: results ruleset
	"""
	g = get_graph(source)
	r = ProvConstraints(g).get_result()
	return r


def format_rule_results(rule_result_set, print_=False):
	"""if any rule fails, the ruleset failed.  However, that could mean
	that the test passed."""
	result_string = ""
	for rule in rule_result_set['rule_results']:
		if rule['passed']:
			result_string = ",".join((result_string, 'Passed: ', rule['id']))
		else:
			result_string = ",".join((result_string, 'Failed: '))
			for msg in rule['fail_reasons']:
				result_string = ",".join((result_string, msg))
	if print_:
		print result_string
	return result_string


# g = get_graph(
# 	'C:\\Users\\ayr016\\stashwork\\Nectar\\unification-generation-f5-FAIL-c23.ttl')
#
# r = ProvConstraints(g).get_result()
#
# for rule in r['rule_results']:
# 	if rule['passed']:
# 		print 'Passed'
# 	else:
# 		print 'Failed: ',
# 		for msg in rule['fail_reasons']:
# 			print msg




# ToDo: merge the code below into the unittest file test_provConstraints.py
testpass = re.compile('.*PASS.*')
testfail = re.compile('.*FAIL.*')

key_constraints = re.compile('.*-c2[23].*') # constraints 22-23
unique = re.compile('.*-c2[4-9].*') # constraints 24-29
cycle = re.compile('.*-c[34][0-9].*') # constraints 30-49
type_constraints = re.compile('.*-c50.*') # constraint 50 only
impossibility = re.compile('.*-c5[1-6].*') # constraints 51-56

response = urllib2.urlopen('https://dvcs.w3.org/hg/prov/raw-file/default/testcases/rdf-tests.txt')
html = response.read()
failreport = []
passreport = []  # https://dvcs.w3.org/hg/prov/raw-file/default/testcases/process.html should report both sets

print datetime.datetime.now()

for line in html.split('\n'):
	print line
	if not line.endswith('.ttl'):
		print 'only testing ttl files'
		continue
	# tests that are supposed to pass:
	if testpass.match(line):
		# print "{0};".format(line)
		r = get_prov_constraint_result(line)
		for rule in r['rule_results']:
			if not rule['passed']:
				failreport.append((line, format_rule_results(rule_result_set=r)))
				break
		passreport.append(line)
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

for entry in failreport:
	print entry
print datetime.datetime.now()