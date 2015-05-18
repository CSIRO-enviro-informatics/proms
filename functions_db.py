import settings

import requests
import json
import rdflib


def db_query(sparql_query):
    data = {'query': sparql_query, 'format': 'json'}
    headers = {'Accept': 'application/json'}
    r = requests.post(settings.FUSEKI_QUERY_URI, data=data, headers=headers)
    return json.loads(r.text)


# TODO: move this to a POST query - there is an error in that I can only get GET to work for SELECT. INSERT POST ok
def db_query_secure(sparql_query):
    auth = (settings.FUSEKI_SECURE_USR, settings.FUSEKI_SECURE_PWD)
    data = {'query': sparql_query, 'format': 'json'}
    headers = {'Accept': 'application/json'}
    r = requests.post(settings.FUSEKI_SECURE_QUERY_URI, auth=auth, data=data, headers=headers)
    try:
        return json.loads(r.text)
    except Exception, e:
        print e.message
        return [False, e.message]


def db_insert(turtle, from_string=False):
    #convert the Turtle into N-Triples
    g = rdflib.Graph()
    if from_string:
        g.parse(data=turtle, format='text/turtle')
    else:
        g.load(turtle, format='n3')

    # SPARQL INSERT
    data = {'update': 'INSERT DATA { ' + g.serialize(format='nt') + ' }'}
    r = requests.post(settings.FUSEKI_SECURE_UPDATE_URI, data=data)
    try:
        if r.status_code != 200 and r.status_code != 201:
            return [False, r.text]
        return [True, r.text]
    except Exception, e:
        print e.message
        return [False, e.message]


def db_insert_secure(turtle, from_string=False):
    #convert the Turtle into N-Triples
    g = rdflib.Graph()
    if from_string:
        g.parse(data=turtle, format='text/turtle')
    else:
        g.load(turtle, format='n3')

    # SPARQL INSERT
    data = {'update': 'INSERT DATA { ' + g.serialize(format='nt') + ' }'}
    auth = (settings.FUSEKI_SECURE_USR, settings.FUSEKI_SECURE_PWD)
    #headers = {'Accept': 'application/json'}
    r = requests.post(settings.FUSEKI_SECURE_UPDATE_URI, data=data, auth=auth)
    try:
        if r.status_code != 200 and r.status_code != 201:
            return [False, r.text]
        return [True, r.text]
    except Exception, e:
        print e.message
        return [False, e.message]


def db_insert_secure_named_graph(turtle, graph_uri, from_string=False):
    #convert the Turtle into N-Triples
    g = rdflib.Graph()
    if from_string:
        g.parse(data=turtle, format='text/turtle')
    else:
        g.load(turtle, format='n3')

    # SPARQL INSERT
    data = {'update': 'INSERT DATA { GRAPH ' + graph_uri + ' { ' + g.serialize(format='nt') + ' } }', format: 'json'}
    auth = (settings.FUSEKI_SECURE_USR, settings.FUSEKI_SECURE_PWD)
    headers = {'Accept': 'text/turtle'}
    try:
        r = requests.post(settings.FUSEKI_SECURE_UPDATE_URI, headers=headers, data=data, auth=auth)
        if r.status_code != 200 and r.status_code != 201:
            return [False, r.text]
        return [True, r.text]
    except Exception, e:
        print e.message
        return [False, e.message]


def get_values_from_sparql_results(results, vars):
    ret = []
    for triple in results['results']['bindings']:
        row = []
        for var in vars:
            row.append(triple[var]['value'])
        ret.append(row)
    return ret
