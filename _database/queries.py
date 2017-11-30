import _config as conf
import requests
import json


def query(sparql_query, format_mimetype='application/sparql-results+json'):
    """ Make a SPARQL query"""
    auth = (conf.SPARQL_AUTH_USR, conf.SPARQL_AUTH_PWD)
    data = {'query': sparql_query}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': format_mimetype
    }
    try:
        r = requests.post(conf.SPARQL_QUERY_URI, auth=auth, data=data, headers=headers, timeout=1)
        return json.loads(r.text)
    except Exception as e:
        raise e


def query_turtle(sparql_query):
    """ Make a SPARQL query with turtle format response"""
    data = {'query': sparql_query, 'format': 'text/turtle'}
    auth = (conf.SPARQL_AUTH_USR, conf.SPARQL_AUTH_PWD)
    headers = {'Accept': 'text/turtle'}
    r = requests.post(conf.SPARQL_QUERY_URI, data=data, auth=auth, headers=headers, timeout=1)
    try:
        return r.content
    except Exception as e:
        raise


def insert(g, named_graph_uri=None):
    """ Securely insert a named graph into the DB"""
    if named_graph_uri is not None:
        data = {'update': 'INSERT DATA { GRAPH <' + named_graph_uri + '> { ' + g.serialize(format='nt').decode('utf-8') + ' } }'}
    else:  # insert into default graph
        data = {'update': 'INSERT DATA { ' + g.serialize(format='nt') + ' }'}
    auth = (conf.SPARQL_AUTH_USR, conf.SPARQL_AUTH_PWD)
    headers = {'Accept': 'text/turtle'}
    try:
        r = requests.post(conf.SPARQL_UPDATE_URI, headers=headers, data=data, auth=auth, timeout=1)
        if r.status_code != 200 and r.status_code != 201:
            raise Exception('The INSERT was not successful. The SPARQL _database\' error message is: ' + r.content)
        return True
    except requests.ConnectionError as e:
        print(str(e))
        raise Exception()


def update(sparql_update_query, format_mimetype='application/sparql-results+json'):
    """ Make a SPARQL update"""
    auth = (conf.SPARQL_AUTH_USR, conf.SPARQL_AUTH_PWD)
    data = {'update': sparql_update_query}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': format_mimetype
    }
    try:
        r = requests.post(conf.SPARQL_UPDATE_URI, auth=auth, data=data, headers=headers, timeout=1)
        return r.text
    except Exception as e:
        raise e
