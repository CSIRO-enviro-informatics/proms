__author__ = 'ayr016'

import requests

import sys
sys.path.insert(0, "..\\proms")
from functions_db import *

class PingTest():
	def __init__(self, uri, headers=[],response_code=200):
		print "ping test uri {0}".format(uri)
		if uri is None or len(uri) == 0:
			self.result = [False,  'URI cannot be None or empty']
		elif not uri.startswith('http://') or len(uri) < 5:
			self.result =  [False, 'URI is not None or empty but does not look like a valid URI']
		else:
			if len(headers)==0:
				r=requests.get(uri)
			else:
				r=requests.get(uri, headers=headers)

			if (r.status_code == response_code):
				self.result = [True, '']
			else:
				self.result = [False, 'Response code {0} is different from desired {1}'.format(r.status_code, response_code)]

	def get_result(self):
		return self.result


if __name__ == "__main__":
	# very basic test of connectivity
	p = PingTest("http://proms-dev.vhirl.net/function/sparql/")
	print p.get_result()