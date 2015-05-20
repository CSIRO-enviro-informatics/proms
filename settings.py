HOME_DIR = '/opt/proms/'
STATIC_DIR = 'static/'
LOGFILE = HOME_DIR + 'proms.log'
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