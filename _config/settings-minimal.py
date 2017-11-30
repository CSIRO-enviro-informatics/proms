import os
import logging
import subprocess

VERSION = subprocess.check_output(["git", "describe"]).split('-')[0].replace('v', '')
BASE_URI = 'http://localhost:5000'
ACTIVITY_BASE_URI = 'http://example.com/activity/'
AGENT_BASE_URI = 'http://example.com/agent/'
ENTITY_BASE_URI = 'http://example.com/entity/'
PERSON_BASE_URI = 'http://example.com/person/'
REPORT_BASE_URI = 'http://example.com/report/'
REPORT_NAMED_GRAPH_BASE_URI = 'http://example.com/report/'
REPORTINGSYSTEM_BASE_URI = 'http://example.com/reportingsystem/'
REPORTINGSYSTEM_NAMED_GRAPH_BASE_URI = 'http://example.com/reportingsystem/'
PINGBACK_BASE_URI = 'http://example.com/pingback/'
PINGBACK_NAMED_GRAPH_BASE_URI = 'http://example.com/pingback/'
PINGBACK_RESULTS_NAMED_GRAPH_BASE_URI = 'http://example.com/pingbackresults/'

HOME_DIR = os.path.dirname(os.path.abspath(__file__))
LOGFILE = APP_DIR + 'proms.log'
LOG_LEVEL = logging.DEBUG
DEBUG = True

#   Internal SPARQL endpoints
SPARQL_QUERY_URI = 'http://localhost:3030/tdb/query'
SPARQL_UPDATE_URI = 'http://localhost:3030/tdb/update'
SPARQL_AUTH_USR = ''  # Ensure this matches any triplestore proxying settings (install-apache.sh)
SPARQL_AUTH_PWD = ''  # Ensure this matches any triplestore proxying settings (install-apache.sh)
SPARQL_TIMEOUT = 5  # Request Timeout in seconds
