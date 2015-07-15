PROMS_LABEL = 'A PROMS Server'
HOME_DIR = '/opt/proms/'
STATIC_DIR = 'static/'
LOGFILE = HOME_DIR + 'proms.log'
HOST = '0.0.0.0'
PORT = 9000
DEBUG = True

PROMS_INSTANCE_NAMESPACE_URI = 'http://localhost/'

FUSEKI_QUERY_URI = 'http://localhost/fuseki/data/query'
FUSEKI_UPDATE_URI = 'http://localhost/fuseki/data/update'

FUSEKI_SECURE_QUERY_URI = 'http://localhost/fuseki/data/query'
FUSEKI_SECURE_UPDATE_URI = 'http://localhost/fuseki/data/update'

FUSEKI_SECURE_USR = 'fusekiusr'
# Make sure this password matches the one entered during Fuseki installation
FUSEKI_SECURE_PWD = 'fusekirocks'
# Request Timeout in seconds
FUSEKI_TIMEOUT = 5

# Pingback strategies to be tried (in order)
PINGBACK_CONFIG = {
	'pingback_strategies': ['known_stores', 'follow_linked_data']
}
# Comma separated list of known PROMS instances that receive pingback
KNOWN_PROMS_INSTANCES = []

DPN_BASE_URI = 'http://sample-dpn-instance.com'

