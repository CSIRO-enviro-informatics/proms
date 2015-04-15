import settings
import requests
import SPARQLWrapper


def db_query(sparql_query):
    sparql = SPARQLWrapper.SPARQLWrapper(settings.FUSEKI_QUERY_URI, returnFormat=SPARQLWrapper.JSON)

    sparql.setQuery(sparql_query)
    sparql.method = 'POST'
    #sparql.requestMethod = 'URLENCODED'

    try:
        return sparql.query().convert()
    except Exception, e:
        print e.message
        return e.message


# TODO: move this to a POST query - there is an error in that I can only get GET to work for SELECT. INSERT POST ok
def db_query_secure(sparql_query):
    sparql = SPARQLWrapper.SPARQLWrapper(settings.FUSEKI_SECURE_QUERY_URI, returnFormat=SPARQLWrapper.JSON)
    sparql.setCredentials(settings.FUSEKI_SECURE_USR, settings.FUSEKI_SECURE_PWD)
    if hasattr(settings, 'FUSEKI_TIMEOUT'):
        sparql.setTimeout(settings.FUSEKI_TIMEOUT)
    sparql.setQuery(sparql_query)
    sparql.method = 'GET'

    try:
        return sparql.query().convert()
    except Exception, e:
        print e.message
        return e.message


def db_insert(turtle, from_string=False):
    #convert the Turtle into N-Triples
    import rdflib
    g = rdflib.Graph()
    if from_string:
        g.parse(data=turtle, format='text/turtle')
    else:
        g.load(turtle, format='n3')

    # SPARQL INSERT
    sparql = SPARQLWrapper.SPARQLWrapper(settings.FUSEKI_UPDATE_URI)
    sparql.setQuery('INSERT DATA { ' + g.serialize(format='nt') + ' }')
    sparql.method = 'POST'

    try:
        return [True, sparql.query()]
    except Exception, e:
        print e.message
        return [False, e.message]


def db_insert_secure(turtle, from_string=False):
    #convert the Turtle into N-Triples
    import rdflib
    g = rdflib.Graph()
    if from_string:
        g.parse(data=turtle, format='text/turtle')
    else:
        g.load(turtle, format='n3')

    # SPARQL INSERT
    sparql = SPARQLWrapper.SPARQLWrapper(settings.FUSEKI_SECURE_UPDATE_URI)
    sparql.setCredentials(settings.FUSEKI_SECURE_USR, settings.FUSEKI_SECURE_PWD)
    sparql.setQuery('INSERT DATA { ' + g.serialize(format='nt') + ' }')
    sparql.method = 'POST'

    try:
        return [True, sparql.query()]
    except Exception, e:
        print e.message
        return e.message



def db_insert_secure_named_graph(turtle, graph_uri, from_string=False):
    #convert the Turtle into N-Triples
    import rdflib
    g = rdflib.Graph()
    if from_string:
        g.parse(data=turtle, format='text/turtle')
    else:
        g.load(turtle, format='n3')

    # SPARQL INSERT
    sparql = SPARQLWrapper.SPARQLWrapper(settings.FUSEKI_SECURE_UPDATE_URI)
    sparql.setCredentials(settings.FUSEKI_SECURE_USR, settings.FUSEKI_SECURE_PWD)
    sparql.setQuery('INSERT DATA { GRAPH ' + graph_uri + ' { ' + g.serialize(format='nt') + ' } }')
    sparql.method = 'POST'
    if graph_uri:
        sparql.addParameter("named-graph-uri", graph_uri)
    try:
        return [True, sparql.query()]
    except Exception, e:
        print e.message
        return e.message



def submit_stardog_query(query):
    uri = settings.PROMS_DB_URI
    qsa = {'query': query}
    h = {'accept': 'application/sparql-results+json'}
    r = requests.get(uri, params=qsa, headers=h, auth=('proms', 'proms'))

    if r.status_code == 200:
        return [True, r.text]
    else:
        return [False, 'ERROR: ' + r.text]


def get_values_from_sparql_results(results, vars):
    ret = []
    for triple in results['results']['bindings']:
        row = []
        for var in vars:
            row.append(triple[var]['value'])
        ret.append(row)

    return ret
