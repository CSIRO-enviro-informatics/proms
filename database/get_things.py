import urllib
from rdflib import Graph
from database import sparqlqueries
from routes.functions_reportingsystems import get_reportingsystem_details_svg, get_reportingsystem_reports_svg


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


def get_agent(agent_uri):
    """ Get an Agent from the provenance database"""

    q = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?label
        WHERE { GRAPH ?g {
            <%(agent_uri)s> a prov:Agent ;
                rdfs:label ?label .
          }
        }
        ''' % {'agent_uri': agent_uri}
    agent = None
    for row in sparqlqueries.query(q)['results']['bindings']:
        agent = {
            'uri': agent_uri,
            'label': row['label']['value']
        }

    return agent


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


def get_reportingsystem(reportingsystem_uri):
    """ Get details for a ReportingSystem
    """
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        SELECT ?t ?fn ?o ?em ?ph ?add ?v
        WHERE {
          <''' + reportingsystem_uri + '''> a proms:ReportingSystem .
          <''' + reportingsystem_uri + '''> rdfs:label ?t .
          OPTIONAL { <''' + reportingsystem_uri + '''> proms:owner ?o . }
          OPTIONAL { <''' + reportingsystem_uri + '''> proms:validation ?v . }
          OPTIONAL { ?o vcard:fn ?fn . }
          OPTIONAL { ?o vcard:hasEmail ?em . }
          OPTIONAL { ?o vcard:hasTelephone ?ph_1 . }
          OPTIONAL { ?ph_1 vcard:hasValue ?ph . }
          OPTIONAL { ?o vcard:hasAddress ?add_1 . }
          OPTIONAL { ?add_1 vcard:locality ?add }
        }
    '''
    reportingsystem_detail = sparqlqueries.query(query)
    ret = {}
    if reportingsystem_detail and 'results' in reportingsystem_detail:
        if len(reportingsystem_detail['results']['bindings']) > 0:
            ret['t'] = reportingsystem_detail['results']['bindings'][0]['t']['value']
            if 'fn' in reportingsystem_detail['results']['bindings'][0]:
                ret['fn'] = reportingsystem_detail['results']['bindings'][0]['fn']['value']
            if 'o' in reportingsystem_detail['results']['bindings'][0]:
                ret['o'] = reportingsystem_detail['results']['bindings'][0]['o']['value']
            if 'em' in reportingsystem_detail['results']['bindings'][0]:
                ret['em'] = reportingsystem_detail['results']['bindings'][0]['em']['value']
            if 'ph' in reportingsystem_detail['results']['bindings'][0]:
                ret['ph'] = reportingsystem_detail['results']['bindings'][0]['ph']['value']
            if 'add' in reportingsystem_detail['results']['bindings'][0]:
                ret['add'] = reportingsystem_detail['results']['bindings'][0]['add']['value']
            if 'v' in reportingsystem_detail['results']['bindings'][0]:
                ret['v'] = reportingsystem_detail['results']['bindings'][0]['v']['value']
            ret['uri'] = reportingsystem_uri

            svg_script = get_reportingsystem_details_svg(ret)
            if svg_script[0] == True:
                rs_script = svg_script[1]
                rs_script += get_reportingsystem_reports_svg(reportingsystem_uri)
                ret['rs_script'] = rs_script
    return ret


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


def get_report(report_uri):
    """ Get details for a a Report (JSON)
    """
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?rt ?l ?id ?rs ?rs_t ?sac ?sac_t ?sat ?eac ?eac_t ?eat
        WHERE {
            GRAPH ?g {
                <''' + report_uri + '''> a ?rt .
                <''' + report_uri + '''> rdfs:label ?l .
                <''' + report_uri + '''> proms:nativeId ?id .
                OPTIONAL { <''' + report_uri + '''> proms:reportingSystem ?rs } .
                OPTIONAL { <''' + report_uri + '''> proms:startingActivity ?sac .
                    ?sac prov:startedAtTime ?sat .
                    ?sac rdfs:label ?sac_t
                } .
                OPTIONAL { <''' + report_uri + '''> proms:endingActivity ?eac .
                    ?eac prov:endedAtTime ?eat .
                    ?eac rdfs:label ?eac_t .
                } .
            }
            OPTIONAL { ?rs rdfs:label ?rs_t }
        }
    '''
    return sparqlqueries.query(query)


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
                UNION
                { ?e a proms:ServiceEntity . }
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
    # TODO: landing page with view options:
    #   wasDerivedFrom, wasGeneratedBy, inv. used, hadPrimarySource, wasAttributedTo, value
    # get the report metadata from DB
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT DISTINCT ?l ?c ?dl ?t ?v ?wat ?wat_name
        WHERE {
            GRAPH ?g {
                <''' + entity_uri + '''> a prov:Entity .
                OPTIONAL { <''' + entity_uri + '''> rdfs:label ?l . }
                OPTIONAL { <''' + entity_uri + '''> dc:created ?c . }
                OPTIONAL { <''' + entity_uri + '''> dcat:downloadURL ?dl . }
                OPTIONAL { <''' + entity_uri + '''> rdfs:label ?t . }
                OPTIONAL { <''' + entity_uri + '''> prov:value ?v . }
                OPTIONAL { <''' + entity_uri + '''> prov:wasAttributedTo ?wat . }
                OPTIONAL { ?wat foaf:name ?wat_name . }
            }
        }
    '''
    return sparqlqueries.query(query)


def get_activities():
    """ Get details of all Activities
    """
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?a ?l
        WHERE {
            GRAPH ?g {
                ?a a prov:Activity .
                ?a rdfs:label ?l
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
                ret['l'] = str(activity['l']['value'])
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
                <''' + activity_uri + '''> a prov:Activity .
                <''' + activity_uri + '''> rdfs:label ?l .
                { ?r proms:startingActivity <''' + activity_uri + '''> . }
                UNION
                { ?r proms:endingActivity <''' + activity_uri + '''> . }
                OPTIONAL { ?r rdfs:label ?rt . }
                OPTIONAL { <''' + activity_uri + '''> rdfs:label ?t . }
                OPTIONAL { <''' + activity_uri + '''> prov:startedAtTime ?sat . }
                OPTIONAL { <''' + activity_uri + '''> prov:endedAtTime ?eat . }
                OPTIONAL { <''' + activity_uri + '''> prov:wasAssociatedWith ?waw . }
                OPTIONAL { ?waw foaf:name ?waw_name . }
            }
        }
    '''
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
