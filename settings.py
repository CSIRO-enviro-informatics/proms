HOME_DIR = '/var/lib/proms/'
STATIC_DIR = 'static/'
LOGFILE = HOME_DIR + 'proms.log'
PORT = 9000
DEBUG = True

#PROMS_INSTANCE_NAMESPACE_URI = 'http://butterfree-bu.nexus.csiro.au/proms/'
PROMS_INSTANCE_NAMESPACE_URI = 'http://localhost:9000/'

FUSEKI_QUERY_URI = 'http://115.146.94.255:3030/data/query'
FUSEKI_UPDATE_URI = 'http://115.146.94.255:3030/data/update'

FUSEKI_SECURE_QUERY_URI = 'http://115.146.94.255/fuseki/data/query'
FUSEKI_SECURE_UPDATE_URI = 'http://115.146.94.255/fuseki/data/update'
FUSEKI_SECURE_USR = 'fusekiusr'
FUSEKI_SECURE_PWD = 'fusekirocks'
# Request Timeout in seconds
FUSEKI_TIMEOUT = 5