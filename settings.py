import sys

SECRET_KEY = 'hello, proms'

ENTITY_BASE_URI = 'http://localhost/entity'
ACTIVITY_BASE_URI = "http://localhost/activity"
AGENT_BASE_URI = "http://localhost/agent"
REPORT_BASE_URI = "http://localhost/report"
REPORTINGSYSTEM_BASE_URI = "http://localhost/reportingsystem"

WEB_SUBFOLDER = ''

if 'dev' in sys.argv or '--dev' in sys.argv:
    PROMS_LABEL = 'A PROMS Server'
    HOME_DIR = '/home/django/BA/proms/'
    STATIC_DIR = 'static/'
    LOGFILE = HOME_DIR + 'proms.log'
    HOST = '0.0.0.0'
    PORT = 9000
    DEBUG = True
    MONGODB="127.0.0.1"

    PROMS_INSTANCE_NAMESPACE_URI = 'http://localhost:9000/'

    FUSEKI_QUERY_URI = 'http://localhost:3030/data/query'
    FUSEKI_UPDATE_URI = 'http://localhost:3030/data/update'

    FUSEKI_SECURE_QUERY_URI = 'http://localhost:3030/data/query'
    FUSEKI_SECURE_UPDATE_URI = 'http://localhost:3030/data/update'

    FUSEKI_SECURE_USR = 'fusekiusr'
    # Make sure this password matches the one entered during Fuseki installation
    FUSEKI_SECURE_PWD = 'password'
    # Request Timeout in seconds
    FUSEKI_TIMEOUT = 5

    # Pingback strategies to be tried (in order)
    PINGBACK_CONFIG = {
        'pingback_strategies': ['known_stores', 'follow_linked_data']
    }
    # Comma separated list of known PROMS instances that receive pingback
    KNOWN_PROMS_INSTANCES = []

    DPN_BASE_URI = 'http://sample-dpn-instance.com'

else:
    PROMS_LABEL = 'A PROMS Server'
    HOME_DIR = '/home/django/BA/proms/'
    STATIC_DIR = 'static/'
    LOGFILE = HOME_DIR + 'proms.log'
    HOST = '0.0.0.0'
    PORT = 9000
    DEBUG = True
    MONGODB="127.0.0.1"

    #PROMS_INSTANCE_NAMESPACE_URI = 'http://localhost/'
    PROMS_INSTANCE_NAMESPACE_URI = 'http://proms-dev1-vc.it.csiro.au/'

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

