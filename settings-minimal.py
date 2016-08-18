ENTITY_BASE_URI = 'http://localhost/id/entity'
ACTIVITY_BASE_URI = "http://localhost/id/activity"
AGENT_BASE_URI = "http://localhost/id/agent"
REPORT_BASE_URI = "http://localhost/id/report"
REPORTINGSYSTEM_BASE_URI = "http://localhost/id/reportingsystem"
WEB_SUBFOLDER = ''
PROMS_INSTANCE_NAMESPACE_URI = 'http://localhost:9000' + WEB_SUBFOLDER
HOME_DIR = 'c:/work/proms/'
STATIC_DIR = 'static/'
LOGFILE = HOME_DIR + 'proms.log'
HOST = '0.0.0.0'
PORT = 9000
DEBUG = True
SPARQL_QUERY_URI = 'http://localhost:3030/data/query'
SPARQL_UPDATE_URI = 'http://localhost:3030/data/update'
SPARQL_AUTH_USR = ''
SPARQL_AUTH_PWD = ''
SPARQL_TIMEOUT = 5
ENTITY_STATE_STORE = HOME_DIR + 'pingbacks/status_recorder/entities.json'
PINGBACK_STRATEGIES = [3]
KNOWN_PROVENANCE_STORE_PINGBACK_ENDPOINTS = [
    'http://fake.com/function/receive_pingback',
]
