#
#   Basic settings
#

#   The IP address that the in-built Flask HTTP server will listen on. Default is 0.0.0.0
#   Irrelevant if PROMS Server is deployed via Apache + mod_wsgi
HOST = '0.0.0.0'

#   The port that the in-built Flask HTTP server will listen on. Default is 9000
#   Irrelevant if PROMS Server is deployed via Apache + mod_wsgi
PORT = 9000

#   This is the URI of this PROMS Server instance. It is the full address of where the service is installed. If running
#   locally without port proxying, as you would for dev, it is likely to be something like http://localhost:9000
#
#   If PROMS Server is installed somewhere it could be http://example.org/service/proms or perhaps
#   http://proms.example.org
#
BASE_URI = 'http://localhost' + str(PORT)

#   If this instance of PROMS Server is installed at a location other than the root of a domain, e.g. at
#   http://example.org/service/proms rather than at http://example.org, then this variable needs to be set to the
#   subfolder. In the example above, the value would be: WEB_SUBFOLDER = '/service/proms'
WEB_SUBFOLDER = ''  # starting slash, no trailing slash

#   These base URIs are the URIs that this instance of PROMS will use to replace http://placeholder.org URIs for the
#   particular classes of objects in incoming ReportingSystems and Reports. E.g.: an incoming Report with the
#   declaration of <http://placeholder.org> a proms:ExternalReport ; will see that triple changed to
#   <{REPORT_BASE_URI + identifier}> a proms:ExternalReport
ACTIVITY_BASE_URI = 'http://example.com/activity/'
AGENT_BASE_URI = 'http://example.com/agent/'
ENTITY_BASE_URI = 'http://example.com/entity/'
PERSON_BASE_URI = 'http://example.com/person/'
REPORT_BASE_URI = 'http://example.com/report/'
REPORTINGSYSTEM_BASE_URI = 'http://example.com/reportingsystem/'


#   This is the location at which PROMS Server is installed on your file system. For Windows this could be something
#   like 'c:/work/proms/', for Linux it could be '/opt/proms/' or '/var/www/proms/'
HOME_DIR = 'c:/work/proms/'  # must end in a slash. Use forward slashes only, even in Windows

#   The directory in which the static content of PROMS Server is stored. Usually 'static/'
STATIC_DIR = 'static/'

#   The PROMS main log file. Usually somewhere in HOME_DIR but need not be
LOGFILE = HOME_DIR + 'proms.log'

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
#   installation) or NginX or similar, these SPARQL endpoints could be something like
#   'http://localhost/sparql/data/query' or 'http://localhost/data/update' or really anything. This setting is set by
#   your proxy server configuration. If using the default installation, this will be set in
#   installation/Ubuntu/install-apache.sh via 2 ProxyPass lines, e.g.:
#
#   ProxyPass   /fuseki/data/query   http://localhost:3030/data/query
#
#   which would dictate a setting here of:
#
#   SPARQL_SECURE_QUERY_URI = 'http://localhost/fuseki/data/query'
#
#   as Apache server is hiding port 3030 from access by proxying to it.
SPARQL_QUERY_URI = 'http://localhost:3030/tdb2/query'
SPARQL_UPDATE_URI = 'http://localhost:3030/tdb2/update'
SPARQL_AUTH_USR = ''  # Ensure this matches any triplestore proxying settings (install-apache.sh)
SPARQL_AUTH_PWD = ''  # Ensure this matches any triplestore proxying settings (install-apache.sh)
SPARQL_TIMEOUT = 5  # Request Timeout in seconds


#
#   PROMS Server v3.1 Pingbacks settings
#
ENTITY_STATE_STORE = HOME_DIR + 'pingbacks/status_recorder/entities.json'
#
# Pingbacks
#
# {'id': 0, 'title': 'No Action'},
# {'id': 1, 'title': 'Given Pingback'},
# {'id': 2, 'title': 'Given Provenance'},
# {'id': 3, 'title': 'Known Provenance Stores'},
# {'id': 4, 'title': 'Pingback Lookup'},
# {'id': 5, 'title': 'Provenance Lookup'}
# Strategy 3: Known Provenance Stores
#
# For strategy 3, we have to have the pingback endpoint URI of the store, not the base URI of the store
# For a PROMS Server of address {PROMS_URI} this is {PROMS_URI}/function/receive_pingback
#
PINGBACK_STRATEGIES = [3]
KNOWN_PROVENANCE_STORE_PINGBACK_ENDPOINTS = [
    'http://fake.com/function/receive_pingback',
]


#
#   PROMS Server v3.2 Secure PROV settings
#
SECRET_KEY = 'hello, proms'
MONGODB = "127.0.0.1"

VERSION = '3.1.0'
