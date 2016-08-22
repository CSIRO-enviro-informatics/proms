import settings
import requests
import json
import rdflib


def query(sparql_query, format_mimetype='application/sparql-results+json'):
    """ Make a secure SPARQL query
    """
    auth = (settings.SPARQL_AUTH_USR, settings.SPARQL_AUTH_PWD)
    data = {'query': sparql_query}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': format_mimetype
    }
    r = requests.post(settings.SPARQL_QUERY_URI, auth=auth, data=data, headers=headers)
    try:
        return json.loads(r.text)
    except Exception, e:
        print e.message
        return [False, e.message]


def query_turtle(sparql_query):
    """ Make a secure query in TURTLE format
    """
    data = {'query': sparql_query, 'format': 'text/turtle'}
    auth = (settings.SPARQL_AUTH_USR, settings.SPARQL_AUTH_PWD)
    headers = {'Accept': 'text/turtle'}
    r = requests.post(settings.SPARQL_QUERY_URI, data=data, auth=auth, headers=headers)
    return r.text


def insert(g):
    """ Make a secure insert into the DB
    """
    # SPARQL INSERT
    data = {'update': 'INSERT DATA { ' + g.serialize(format='nt') + ' }'}
    auth = (settings.SPARQL_AUTH_USR, settings.SPARQL_AUTH_PWD)
    #headers = {'Accept': 'application/json'}
    r = requests.post(settings.SPARQL_UPDATE_URI, data=data, auth=auth)
    try:
        if r.status_code != 200 and r.status_code != 201:
            return [False, r.text]
        return [True, r.text]
    except Exception, e:
        print e.message
        return [False, e.message]


# TODO: repalce insert & insert_named_graph with one with a default param, graph_uri == None
def insert_named_graph(g, graph_uri):
    """ Securely insert a named graph into the DB
    """
    # SPARQL INSERT
    data = {'update': 'INSERT DATA { GRAPH <' + graph_uri + '> { ' + g.serialize(format='nt') + ' } }', format: 'json'}
    auth = (settings.SPARQL_AUTH_USR, settings.SPARQL_AUTH_PWD)
    headers = {'Accept': 'text/turtle'}
    try:
        r = requests.post(settings.SPARQL_UPDATE_URI, headers=headers, data=data, auth=auth)
        if r.status_code != 200 and r.status_code != 201:
            return [False, r.text]
        return [True, r.text]
    except Exception, e:
        print e.message
        return [False, e.message]
