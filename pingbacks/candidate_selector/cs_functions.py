import requests


def get_report_uri_base(g):
    """
    Gets base URI of the PROMS Report. Only External & Internal reports allowed. Only hash URIs allowed.

    :param graph: the de-serialised graph of the inbound report contents
    :return: string, report URI base, including hash
    """
    q = '''
            PREFIX proms: <http://promsns.org/def/proms#>
            SELECT ?b
            WHERE {
                {?r a proms:ExternalReport .}
                UNION
                {?r a proms:InternalReport .}
                BIND(STRBEFORE(STR(?r), "#" ) AS ?b)
            }
          '''
    b = ''
    for triple in g.query(q):
        b = str(triple['b'])
    return b + '#'


def dereference_entity(entity_uri):
    r = requests.get(entity_uri, allow_redirects=True)
    if r.status_code == 200:
        return True
    else:
        return False


def get_entity_rdf(entity_uri):
    r = requests.get(entity_uri,
                     allow_redirects=True,
                     headers={'Accept': 'text/turtle, application/rdf+xml, application/ld+json'})
    if r.status_code == 200:
        return [True, r.text]
    else:
        return [False, r.text]


def get_entities_for_pingbacks(g):
    base_uri = get_report_uri_base(g)
    q = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?e ?el
        WHERE {
            # Criteria 1 - inferencing
            #?c rdfs:subClassOf* prov:Entity .
            #?e rdf:type ?c .

            # Criteria 1 - static
            { ?e a prov:Entity . }
            UNION
            { ?e a prov:Collection . }
            UNION
            { ?e a prov:Plan . }
            UNION
            { ?e a <http://promsns.org/def/proms#ServiceEntity> . }

            ?e  rdfs:label  ?el .

            # Criteria 2
            MINUS {?a  prov:generated ?e .}
            # Criteria 2
            MINUS {?e prov:wasGeneratedBy ?a .}
            # Criteria 3
            MINUS {?e prov:wasDerivedFrom ?e2 .}'''
    if base_uri != '':
        q += '''
            # Criteria 4
            FILTER regex(STR(?e), "^((?!''' + get_report_uri_base(g) + ''').)*$", "i")
        '''
    q+='''
        }
        ORDER BY ASC(?el)
    '''
    actual_results = []
    for triple in g.query(q):
        actual_results.append(str(triple['e']))

    return actual_results


def get_entities_for_pingbacks2(g):
    q = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?e ?el ?b
        WHERE {
            # Criteria 1 - inferencing
            #?c rdfs:subClassOf* prov:Entity .
            #?e rdf:type ?c .

            # Criteria 1 - static
            { ?e a prov:Entity . }
            UNION
            { ?e a prov:Collection . }
            UNION
            { ?e a prov:Plan . }
            UNION
            { ?e a <http://promsns.org/def/proms#ServiceEntity> . }

            ?e  rdfs:label  ?el .

            # Criteria 2
            MINUS {?a  prov:generated ?e .}
            MINUS {?e prov:wasGeneratedBy ?a .}

            # Criteria 3
            MINUS {?e prov:wasDerivedFrom ?e2 .}
            MINUS {?e prov:wasRevisionOf ?e2 .}  # could be others

            # Criteria 4
            {
                SELECT ?b
                WHERE {
                    {?r a proms:ExternalReport .}
                    UNION
                    {?r a proms:InternalReport .}
                    BIND(STRBEFORE(STR(?r), "#" ) AS ?b)
                }
            }
            FILTER regex(STR(?e), CONCAT("^((?!", ?b, ").)*$"), "i")
        }
        ORDER BY ASC(?el)
    '''
    actual_results = []
    for triple in g.query(q):
        actual_results.append(str(triple['e']))

    return actual_results