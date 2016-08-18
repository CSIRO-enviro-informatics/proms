import settings

import requests
import json
import rdflib


def db_query(sparql_query):
    """ Make a non-secure SPARQL query
    """
    data = {'query': sparql_query, 'format': 'json'}
    headers = {'Accept': 'application/sparql-results+json'}
    r = requests.post(settings.SPARQL_QUERY_URI, data=data, headers=headers)
    return json.loads(r.text)


def db_query_secure(sparql_query, format_mimetype='application/sparql-results+json'):
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


def db_query_secure_turtle(sparql_query):
    """ Make a secure query in TURTLE format
    """
    data = {'query': sparql_query, 'format': 'text/turtle'}
    auth = (settings.SPARQL_AUTH_USR, settings.SPARQL_AUTH_PWD)
    headers = {'Accept': 'text/turtle'}
    r = requests.post(settings.SPARQL_QUERY_URI, data=data, auth=auth, headers=headers)
    return r.text


def db_insert(turtle, from_string=False):
    """ Make a non-secure insert into the DB
    """
    #convert the Turtle into N-Triples
    g = rdflib.Graph()
    if from_string:
        g.parse(data=turtle, format='text/turtle')
    else:
        g.load(turtle, format='n3')

    # SPARQL INSERT
    data = {'update': 'INSERT DATA { ' + g.serialize(format='nt') + ' }'}
    r = requests.post(settings.SPARQL_UPDATE_URI, data=data)
    try:
        if r.status_code != 200 and r.status_code != 201:
            return [False, r.text]
        return [True, r.text]
    except Exception, e:
        print e.message
        return [False, e.message]


def db_insert_secure(turtle, from_string=False):
    """ Make a secure insert into the DB
    """
    #convert the Turtle into N-Triples
    g = rdflib.Graph()
    try:
        if from_string:
            g.parse(data=turtle, format='text/turtle')
        else:
            g.load(turtle, format='n3')
    except Exception, e:
        print e.message
        return [False, e.message]

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


def db_insert_secure_named_graph(turtle, graph_uri, from_string=False):
    """ Securely insert a named graph into the DB
    """
    #convert the Turtle into N-Triples
    g = rdflib.Graph()
    if from_string:
        g.parse(data=turtle, format='text/turtle')
    else:
        g.load(turtle, format='n3')

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
