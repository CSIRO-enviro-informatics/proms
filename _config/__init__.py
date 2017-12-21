import os
from os.path import dirname, realpath, join, abspath
import logging
import subprocess

#   This is the location at which PROMS Server is installed on your file system. For Windows this could be something
#   like 'c:/work/proms/', for Linux it could be '/opt/proms/' or '/var/www/proms/'
# APP_DIR = 'c:/work/proms/'  # must end in a slash. Use forward slashes only, even in Windows
APP_DIR = dirname(dirname(realpath(__file__)))
TEMPLATES_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'templates')
STATIC_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'static')
#   The PROMS main log file. Usually somewhere in APP_DIR but need not be
LOGFILE = APP_DIR + 'proms.log'

# the version of this PROMS instance is taken from the latest tag of the Git repo
cwd = os.path.dirname(os.path.realpath(__file__))
VERSION = subprocess.check_output(["git", "describe"], cwd=cwd).decode('utf-8').split('-')[0].replace('v', '')

#
#   Basic settings
#

#   This is the URI of this PROMS Server instance. It is the full address of where the service is installed. If running
#   locally without port proxying, as you would for dev, it is likely to be something like http://localhost:9000
#
#   If PROMS Server is installed somewhere it could be http://example.org/service/proms or perhaps
#   http://proms.example.org
#
BASE_URI = 'http://localhost:5000'


#   These base URIs are the URIs that this instance of PROMS will use to replace http://placeholder.org URIs for the
#   particular classes of objects in incoming ReportingSystems and Reports. E.g.: an incoming Report with the
#   declaration of <http://placeholder.org> a proms:ExternalReport ; will see that triple changed to
#   <{REPORT_BASE_URI + identifier}> a proms:ExternalReport
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

#   the log level currently in use
LOG_LEVEL = logging.DEBUG

#   Flask debug mode. True for testing, False for production.
#   Irrelevant if PROMS Server is deployed via Apache + mod_wsgi
DEBUG = True


#   Internal SPARQL endpoints
#
#   These settings are used to tell PROMS Server where to find the query endpoints of the triplestore that it needs to
#   use in order to store and access provenance data in RDF.
#
#   PROMS Server is usually run with Fuseki2 (https://jena.apache.org/documentation/fuseki2/) but any SPARQL 1.1 store
#   could be used.
#
#   A query (read only) and an update (read/write) endpoint must be defined. Secure or non-secure endpoints can be
#   used but security is set by a proxy layer (perhaps Apache), not in PROMS Server. If security is use (it should be)
#   then the settings for username and password should be put here. This will ensure that the triplestore is only
#   accessed via PROMS Server's various functions.
#
#   If using PROMS Server without a proxy server, say on a local machine for dev purposes, these endpoints will point
#   directly to the SPARQL endpoints of the SPARQL service you use. If using Fuseki2, this will, by default, be
#   'http://localhost:3030/data/query' & 'http://localhost:3030/data/update'
#
#   If using PROMS Server behind a proxy server, as is usually the case when deployed on a VM with Apache (default
#   _installation) or NginX or similar, these SPARQL endpoints could be something like
#   'http://localhost/sparql/data/query' or 'http://localhost/data/update' or really anything. This setting is set by
#   your proxy server configuration. If using the default _installation, this will be set in
#   _installation/scripts/install-apache.sh via 2 ProxyPass lines, e.g.:
#
#   ProxyPass   /fuseki/data/query   http://localhost:3030/data/query
#
#   which would dictate a setting here of:
#
#   SPARQL_SECURE_QUERY_URI = 'http://localhost/fuseki/data/query'
#
#   as Apache server is hiding port 3030 from access by proxying to it.
SPARQL_QUERY_URI = 'http://proms.promsns.org/fuseki/proms/query'
SPARQL_UPDATE_URI = 'http://proms.promsns.org/fuseki/proms/update'
SPARQL_AUTH_USR = 'fuseki'  # Ensure this matches any triplestore proxying settings (install-apache.sh)
SPARQL_AUTH_PWD = 'provenator'  # Ensure this matches any triplestore proxying settings (install-apache.sh)
SPARQL_TIMEOUT = 5  # Request Timeout in seconds

MODULES = {
    'ldapi': {
        'enabled': True,
        'path': join(APP_DIR, 'modules', 'ldapi'),
    },
    'pingbacks': {
        'enabled': True,
        'path': join(APP_DIR, 'modules', 'pingbacks'),
    },
    'rulesets': {
        'enabled': True,
        'path': join(APP_DIR, 'modules', 'rulesets'),
        'rulesets': {
            'reports': {
                'enabled': True
            },
            'reportingsystems': {
                'enabled': True
            },
            'pingbacks': {
                'enabled': False
            }
        }
    }
}
