import requests
import imp
settings = imp.load_source('', 'c:/work/proms/__init__.py')


def db_delete_all_secure():
    """ Make a secure delete of all triples in the DB
    """
    # SPARQL  all named graphs
    data = {'update': 'DELETE WHERE { GRAPH ?g {?s ?p ?o}}'}
    auth = (settings.FUSEKI_SECURE_USR, settings.FUSEKI_SECURE_PWD)
    r = requests.post(settings.FUSEKI_SECURE_UPDATE_URI, data=data, auth=auth)

    # SPARQL DELETE all non-named graphs (default graph)
    data = {'update': 'DELETE WHERE {?s ?p ?o}'}
    auth = (settings.FUSEKI_SECURE_USR, settings.FUSEKI_SECURE_PWD)
    r = requests.post(settings.FUSEKI_SECURE_UPDATE_URI, data=data, auth=auth)
    try:
        if r.status_code != 200 and r.status_code != 201:
            return [False, r.text]
        return [True, r.text]
    except Exception as e:
        print(e.message)
        return [False, e.message]


result = db_delete_all_secure()
if result[0]:
    print('cleared')
else:
    print('ERROR: ' + result[1])
