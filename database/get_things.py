import urllib

from rdflib import Graph

from database import sparqlqueries


def get_agents():
    """ Get all Agents in the provenance database"""

    q = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?ag ?label
        WHERE { GRAPH ?g {
            ?ag a prov:Agent ;
                rdfs:label ?label .
          }
        }
        '''
    agents = []
    for row in sparqlqueries.query(q)['results']['bindings']:
        agents.append({
            'uri': row['ag']['value'],
            'label': row['label']['value']
        })

    return agents


def get_reportingsystems():
    """ Get all ReportingSystem details"""
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?rs ?t
        WHERE {
          ?rs a proms:ReportingSystem .
          ?rs rdfs:label ?t .
        }
    '''
    reportingsystems = sparqlqueries.query(query)
    reportingsystem_items = []
    # Check if nothing is returned
    if reportingsystems and 'results' in reportingsystems:
        for reportingsystem in reportingsystems['results']['bindings']:
            ret = {}
            ret['rs'] = urllib.quote(str(reportingsystem['rs']['value']))
            ret['rs_u'] = str(reportingsystem['rs']['value'])
            if reportingsystem.get('t'):
                ret['t'] = str(reportingsystem['t']['value'])
            reportingsystem_items.append(ret)
    return reportingsystem_items


def get_reports():
    """ Get details of all Reports
    """
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT DISTINCT ?r ?t
        WHERE {
            GRAPH ?g {
                { ?r a proms:BasicReport . }
                UNION
                { ?r a proms:ExternalReport . }
                UNION
                { ?r a proms:InternalReport . }
                ?r rdfs:label ?t
            }
        }
        ORDER BY ?r
    '''
    reports = sparqlqueries.query(query)

    report_items = []
    # Check if nothing is returned
    if reports and 'results' in reports:
        for report in reports['results']['bindings']:
            ret = {}
            ret['r'] = urllib.quote(str(report['r']['value']))
            ret['r_u'] = str(report['r']['value'])
            if report.get('t'):
                ret['t'] = str(report['t']['value'])
            report_items.append(ret)
    return report_items


def get_class_object_graph(uri):
    """
    Returns the graph of an object in the graph database

    :param uri: the URI of something in the graph database
    :return: an RDF Graph
    """
    if uri is not None:
        r = sparqlqueries.query_turtle(
            'CONSTRUCT { <' + uri + '> ?p ?o } WHERE { <' + uri + '> ?p ?o }'
        )
        # a uri query string argument was supplied was supplied but it was not the URI of something in the graph
        g = Graph().parse(data=r, format='turtle')
        if len(g) == 0:
            # try a named graph
            r = sparqlqueries.query_turtle(
                'CONSTRUCT { <' + uri + '> ?p ?o } WHERE { GRAPH ?g { <' + uri + '> ?p ?o }}'
            )
            # a uri query string argument was supplied was supplied but it was not the URI of something in the graph
            g = Graph().parse(data=r, format='turtle')

            if len(g) == 0:
                # nothing found
                return False
            else:
                return g
        else:
            return g
        # no uri query string argument was supplied
    else:
        return False


def get_entities():
    """ Get details for all Entities
    """
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT DISTINCT ?e ?l
        WHERE {
            GRAPH ?g {
                { ?e a prov:Entity . }
                UNION
                { ?e a prov:Plan . }
                OPTIONAL { ?e rdfs:label ?l . }
            }
        }
        ORDER BY ?e
    '''
    entities = sparqlqueries.query(query)
    entity_items = []
    # Check if nothing is returned
    if entities and 'results' in entities:
        for entity in entities['results']['bindings']:
            ret = {}
            ret['e'] = urllib.quote(str(entity['e']['value']))
            ret['e_u'] = str(entity['e']['value'])
            if entity.get('l'):
                ret['l'] = str(entity['l']['value'])
            entity_items.append(ret)
    return entity_items


def get_entity(entity_uri):
    """ Get details for an Entity (JSON)
    """
    # TODO: landing page with model options:
    #   wasDerivedFrom, wasGeneratedBy, inv. used, hadPrimarySource, wasAttributedTo, value
    # get the report metadata from DB
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT DISTINCT ?l ?c ?dl ?label ?v ?wat ?wat_name
        WHERE {
            GRAPH ?g {
                <%(entity_uri)s> a prov:Entity .
                OPTIONAL { <%(entity_uri)s> rdfs:label ?l . }
                OPTIONAL { <%(entity_uri)s'> dc:created ?c . }
                OPTIONAL { <%(entity_uri)s> dcat:downloadURL ?dl . }
                OPTIONAL { <%(entity_uri)s> rdfs:label ?label . }
                OPTIONAL { <%(entity_uri)s> prov:value ?v . }
                OPTIONAL { <%(entity_uri)s> prov:wasAttributedTo ?wat . }
                OPTIONAL { ?wat foaf:name ?wat_name . }
            }
        }
    ''' % {'entity_uri': entity_uri}
    return sparqlqueries.query(query)


def get_activities():
    """ Get details of all Activities
    """
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?a ?lable
        WHERE {
            GRAPH ?g {
                ?a a prov:Activity .
                ?a rdfs:label ?lable
            }
        }
        ORDER BY ?a
    '''
    activities = sparqlqueries.query(query)
    activity_items = []
    if activities and 'results' in activities:
        for activity in activities['results']['bindings']:
            ret = {}
            ret['a'] = urllib.quote(str(activity['a']['value']))
            ret['a_u'] = str(activity['a']['value'])
            if activity.get('l'):
                ret['l'] = str(activity['label']['value'])
            activity_items.append(ret)
    return activity_items


def get_activity(activity_uri):
    """ Get the details of an Activity (JSON)
    """
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT DISTINCT ?l ?t ?sat ?eat ?waw ?r ?rt
        WHERE {
            GRAPH ?g {
                <%(activity_uri)s> a prov:Activity .
                <%(activity_uri)s> rdfs:label ?l .
                { ?r proms:startingActivity <%(activity_uri)s> . }
                UNION
                { ?r proms:endingActivity <%(activity_uri)s> . }
                OPTIONAL { ?r rdfs:label ?rt . }
                OPTIONAL { <%(activity_uri)s> rdfs:label ?t . }
                OPTIONAL { <%(activity_uri)s> prov:startedAtTime ?sat . }
                OPTIONAL { <%(activity_uri)s> prov:endedAtTime ?eat . }
                OPTIONAL { <%(activity_uri)s> prov:wasAssociatedWith ?waw . }
                OPTIONAL { ?waw foaf:name ?waw_name . }
            }
        }
    '''  % {'activity_uri': activity_uri}
    return sparqlqueries.query(query)


def get_report_rdf(report_uri):
    """ Get Report details as RDF
    """
    query = '''
        DESCRIBE * WHERE { GRAPH <''' + report_uri + '''> { ?s ?p ?o } FILTER ( ?p != <http://promsns.org/def/proms#reportingSystem> ) }
    '''
    return sparqlqueries.query_turtle(query)


def get_class_register(class_uri):
    q = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?uri ?label
        WHERE {
            GRAPH ?g {
                ?uri a <%(class_uri)s> ;
                    rdfs:label ?label .
            }
        }
        ORDER BY ?label
    ''' % {'class_uri': class_uri}
    instances = []
    for r in sparqlqueries.query(q)['results']['bindings']:
        instances.append({
            'uri': r['uri']['value'],
            'label': r['label']['value']
        })

    return instances
