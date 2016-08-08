import sys

SECRET_KEY = 'hello, proms'

ENTITY_BASE_URI = 'http://localhost/id/entity'
ACTIVITY_BASE_URI = "http://localhost/id/activity"
AGENT_BASE_URI = "http://localhost/id/agent"
REPORT_BASE_URI = "http://localhost/id/report"
REPORTINGSYSTEM_BASE_URI = "http://localhost/id/reportingsystem"

WEB_SUBFOLDER = ''  # starting slash, no trailing slash

PROMS_LABEL = 'A PROMS Server'
HOME_DIR = 'c:/work/proms'
STATIC_DIR = 'static/'
LOGFILE = HOME_DIR + 'proms.log'
HOST = '0.0.0.0'
PORT = 9000
DEBUG = True
MONGODB = "127.0.0.1"

PROMS_INSTANCE_NAMESPACE_URI = 'http://localhost:9000' + WEB_SUBFOLDER

FUSEKI_QUERY_URI = 'http://localhost:3030/data/query'
FUSEKI_UPDATE_URI = 'http://localhost:3030/data/update'

FUSEKI_SECURE_QUERY_URI = 'http://localhost:3030/data/query'
FUSEKI_SECURE_UPDATE_URI = 'http://localhost:3030/data/update'

FUSEKI_SECURE_USR = 'fusekiusr'
# Make sure this password matches the one entered during Fuseki installation
FUSEKI_SECURE_PWD = 'fusekirocks'
# Request Timeout in seconds
FUSEKI_TIMEOUT = 5

# Pingback settings
ENTITY_STATE_STORE = HOME_DIR + 'pingbacks/status_recorder/entities.json'
#
# Pingbacks
#
#{'id': 0, 'title': 'No Action'},
#{'id': 1, 'title': 'Given Pingback'},
#{'id': 2, 'title': 'Given Provenance'},
#{'id': 3, 'title': 'Known Provenance Stores'},
#{'id': 4, 'title': 'Pingback Lookup'},
#{'id': 5, 'title': 'Provenance Lookup'}
# Strategy 3: Known Provenance Stores
#
# For strategy 3, we have to have the pingback endpoint URI of the store, not the base URI of the store
# For a PROMS Server of address {PROMS_URI} this is {PROMS_URI}/function/receive_pingback
#
PINGBACK_STRATEGIES = [3]
KNOWN_PROVENANCE_STORE_PINGBACK_ENDPOINTS = [
    'http://fake.com/function/receive_pingback',
]

