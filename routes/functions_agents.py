import urllib
import functions_sparqldb
import settings


def get_agents_dict():
    """ Get all Person details
    """
    #query = '''
    #    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    #    PREFIX prov: <http://www.w3.org/ns/prov#>
    #    SELECT DISTINCT ?ag ?n
    #    WHERE {
    #        GRAPH ?g {
    #            {
    #                { ?e a prov:Entity . }
    #                UNION
    #                { ?e a prov:Plan . }
    #                ?e prov:wasAttributedTo ?ag .
    #                OPTIONAL{ ?ag foaf:familyName ?n . }
    #            }
    #            UNION
    #            {
    #                ?a a prov:Activity .
    #                ?a prov:wasAssociatedWith ?ag .
    #                OPTIONAL{ ?ag foaf:familyName ?n . }
    #            }
    #            UNION
    #            {
    #                ?ag1 a prov:Agent .
    #                ?ag1 prov:actedOnBehalfOf ?ag .
    #                OPTIONAL{ ?ag foaf:familyName ?n . }
    #            }
    #        }
    #    }
    #    '''

    query = '''
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT DISTINCT ?ag ?n ?fn ?em
        WHERE {

                {

                    ?ag foaf:familyName ?n .
                    ?ag foaf:givenName ?fn .
                    ?ag foaf:mbox ?em .
                }
                UNION
                {
                    ?a a prov:Activity .
                    ?a prov:wasAssociatedWith ?ag .
                    OPTIONAL{ ?ag foaf:name ?n . }
                }
                UNION
                {
                    ?ag1 a prov:Person .
                    ?ag1 prov:actedOnBehalfOf ?ag .
                    OPTIONAL{ ?ag foaf:name ?n . }
                }
        }
        '''


#   agents = functions_db.db_query_secure(query)
    agents = functions_sparqldb.query(query)

    agent_items = []
    if agents and 'results' in agents:
        for agent in agents['results']['bindings']:
            ret = {}
            ret['ag'] = urllib.quote(str(agent['ag']['value']))
            ret['ag_u'] = str(agent['ag']['value'])
            if agent.get('n'):
                ret['n'] = str(agent['n']['value'])
            if agent.get('fn'):
                ret['fn'] = str(agent['fn']['value'])
            if agent.get('em'):
                ret['em'] = str(agent['em']['value'])
            agent_items.append(ret)
    return agent_items


def get_agent(agent_uri):
    """ Get Person details (JSON)
    """
    query = '''
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT DISTINCT (<''' + agent_uri + '''> AS ?ag) ?n ?ag2
        WHERE {
            GRAPH ?g {
                {
                    { ?e a prov:Entity . }
                    UNION
                    { ?e a prov:Plan . }
                    OPTIONAL{ ?e prov:wasAttributedTo <''' + agent_uri + '''> . }
                    OPTIONAL{ <''' + agent_uri + '''> foaf:name ?n . }
                    OPTIONAL{ <''' + agent_uri + '''> prov:actedOnBehalfOf ?ag2 . }
                }
                UNION
                {
                    ?e a prov:Activity .
                    OPTIONAL{ ?e prov:wasAssociatedWith <''' + agent_uri + '''> . }
                    OPTIONAL{ <''' + agent_uri + '''> foaf:name ?n . }
                    OPTIONAL{ <''' + agent_uri + '''> prov:actedOnBehalfOf ?ag2 . }
                }
                UNION
                {
                    ?aoo a prov:Person .
                    ?aoo prov:actedOnBehalfOf <''' + agent_uri + '''> .
                    OPTIONAL{ <''' + agent_uri + '''> foaf:name ?n . }
                }
                UNION
                {
                    <''' + agent_uri + '''> a prov:Person .
                    OPTIONAL{ <''' + agent_uri + '''> foaf:name ?n . }
                    OPTIONAL{ <''' + agent_uri + '''> prov:actedOnBehalfOf ?ag2 . }
                }
            }
        }
        '''
    return functions_sparqldb.query(query)


def get_agent_dict(agent_uri):
    """ Get Person details (dict)
    """
    agent_detail = get_agent(agent_uri)
    ret = {}
    if agent_detail and 'results' in agent_detail and len(agent_detail['results']['bindings']) > 0:
        ret['uri'] = agent_uri
        ret['uri_html'] = urllib.quote(agent_uri)
        if 'n' in agent_detail['results']['bindings'][0]:
            ret['n'] = agent_detail['results']['bindings'][0]['n']['value']
        else:
            ret['n'] = agent_uri
        if 'ag2' in agent_detail['results']['bindings'][0]:
            ret['ag2'] = agent_detail['results']['bindings'][0]['ag2']['value']
        # TODO: Re-enable when it's more than just the Person being displayed
        svg_script = get_agent_details_svg(ret)
        if svg_script[0]:
            a_script = svg_script[1]
            a_script += get_agent_was_attributed_to_svg(agent_uri)
            a_script += get_agent_was_associated_with_svg(agent_uri)
            ret['a_script'] = a_script
    return ret


def get_agent_rdf(agent_uri):
    """ Get Person details as RDF
    """
    agent = '''@prefix prov:   <http://www.w3.org/ns/prov#> .
<''' + agent_uri + '''>
    a   prov:Person;
    '''
    return agent


def get_agent_details_svg(agent_dict):
    """ Construct the SVG code for an Person
    """
    a_uri = agent_dict.get('uri')
    if agent_dict.get('n'):
        a_label = agent_dict.get('n')
    else:
        aLabel = a_uri
        aLabel = aLabel.split('#')
        if len(aLabel) < 2:
            aLabel = a_uri.split('/')
        name = aLabel[-1]
    script = '''
        var aLabel = "''' + a_label + '''";
        var agent = addAgent(310, 200, aLabel, "");
    '''

    #print actedOnBehalfOf, if it has one
    if agent_dict.get('ag2'):
        agent_uri = agent_dict.get('ag2')
        agent_uri_encoded = urllib.quote(agent_uri)
        agent_name = agent_uri
        agent_name = agent_name.split('#')
        if len(agent_name) < 2:
            agent_name = agent_uri.split('/')
        agent_name = agent_name[-1]
        script += '''
            var agentAOBO = addAgent(310, 5, "''' + agent_name + '''", "''' + settings.WEB_SUBFOLDER + "/id/agent/?uri=" + agent_uri_encoded + '''");
            addLink(agent, agentWOBO, "prov:actedOnBehalfOf", RIGHT);
        '''
    return [True, script]


def get_agent_was_attributed_to_svg(agent_uri):
    """ Construct the SVG code for the prov:wasAttributedTo Entities of an Person
    """
    script = ''
    query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT DISTINCT ?e ?t
WHERE {
    GRAPH ?g {
        { ?e a prov:Entity .}
        UNION
        { ?e a prov:Plan .}
        ?e prov:wasAttributedTo <''' + agent_uri + '''> ;
        OPTIONAL { ?e rdfs:label ?t . }
    }
}
    '''
    entity_results = functions_sparqldb.query(query)

    if entity_results and 'results' in entity_results:
        wat = entity_results['results']
        if len(wat['bindings']) == 1:
            if wat['bindings'][0].get('t'):
                title = wat['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wat['bindings'][0]['e']['value'])
            script += '''
                entityLabel = "''' + title + '''";
                entityUri = "''' + settings.WEB_SUBFOLDER + '''/id/entity/?uri=''' + uri_encoded + '''";
                var entityWAT = addEntity(385, 430, entityLabel, entityUri);
                addLink(entity, entityWAT, "prov:wasAttributedTo", RIGHT);
            '''
        elif len(wat['bindings']) > 1:
            # TODO: Check query
            query_encoded = urllib.quote(query)
            script += '''
                var entityWAT1 = addEntity(395, 440, "", "");
                var entityWAT2 = addEntity(390, 435, "", "");
                var entityWATN = addEntity(385, 430, "Multiple Entities, click here to search", "''' + settings.WEB_SUBFOLDER + "/function/sparql/?query=" + query_encoded + '''");
                addLink(agent, entityWATN, "prov:wasAttributedTo", RIGHT);
            '''
        else:
            # do nothing as no Activities found
            pass
    else:
        # we have a fault
        script += '''
            var addEntity(550, 200, "There is a fault with retrieving Activities that may have used this Entity", "");
        '''
    return script


def get_agent_was_associated_with_svg(agent_uri):
    """ Construct the SVG code for the prov:wasAssociatedWith Activities of an Person
    """
    script = ''
    query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT DISTINCT ?a ?t
WHERE {
    GRAPH ?g {
        { ?a a prov:Activity . }
        ?a prov:wasAssociatedWith <''' + agent_uri + '''> ;
        OPTIONAL { ?a rdfs:label ?t . }
    }
}
    '''
    activity_results = functions_sparqldb.query(query)

    if activity_results and 'results' in activity_results:
        waw = activity_results['results']
        if len(waw['bindings']) == 1:
            if waw['bindings'][0].get('t'):
                title = waw['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(waw['bindings'][0]['a']['value'])
            script += '''
                activityLabel = "''' + title + '''";
                activityUri = "''' + settings.WEB_SUBFOLDER + '''/id/activity/?uri=''' + uri_encoded + '''";
                var activityWAW = addActivity(5, 200, activityLabel, activityUri);
                addLink(agent, activityWAW, "prov:wasAssociatedWith", TOP);
            '''
        elif len(waw['bindings']) > 1:
            # TODO: Check query
            query_encoded = urllib.quote(query)
            script += '''
                var activityWAW1 = addActivity(15, 210, "", "");
                var activityWAW2 = addActivity(10, 205, "", "");
                var activityWAWN = addActivity(5, 200, "Multiple Activities, click here to search", "''' + settings.WEB_SUBFOLDER + "/function/sparql/?query=" + query_encoded + '''");
                addLink(agent, activityWAWN, "prov:wasAssociatedWith", TOP);
            '''
        else:
            # do nothing as no Activities found
            pass
    else:
        # we have a fault
        script += '''
            var activityUsedFaultText = addActivity(5, 200, "There is a fault with retrieving Activities that may be associated with this Person", "");
        '''
    return script
