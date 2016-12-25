import urllib

import settings
from database import sparqlqueries
from database.get_things import get_entity


def get_entity_dict(entity_uri):
    """ Get details for an Entity (dict)
    """
    entity_detail = get_entity(entity_uri)
    ret = {}
    if entity_detail and 'results' in entity_detail:
        if len(entity_detail['results']['bindings']) > 0:
            ret['uri'] = entity_uri
            ret['uri_html'] = urllib.quote(entity_uri)
            if('l' in entity_detail['results']['bindings'][0]):
                ret['l'] = entity_detail['results']['bindings'][0]['l']['value']
            if('c' in entity_detail['results']['bindings'][0]):
                ret['c'] = entity_detail['results']['bindings'][0]['c']['value']
            if('dl' in entity_detail['results']['bindings'][0]):
                ret['dl'] = entity_detail['results']['bindings'][0]['dl']['value']
            if('t' in entity_detail['results']['bindings'][0]):
                ret['t'] = entity_detail['results']['bindings'][0]['t']['value']
            if('v' in entity_detail['results']['bindings'][0]):
                ret['v'] = entity_detail['results']['bindings'][0]['v']['value']
            if('wat' in entity_detail['results']['bindings'][0]):
                ret['wat'] = entity_detail['results']['bindings'][0]['wat']['value']
            if('wat_name' in entity_detail['results']['bindings'][0]):
                ret['wat_name'] = entity_detail['results']['bindings'][0]['wat_name']['value']
            svg_script = get_entity_details_svg(ret)
            if svg_script[0] == True:
                e_script = svg_script[1]
                e_script += get_entity_activity_wgb_svg(entity_uri)
                e_script += get_entity_activity_used_svg(entity_uri)
                e_script += get_entity_entity_wdf_svg(entity_uri)
                ret['e_script'] = e_script
    return ret


def get_entity_rdf(entity_uri):
    """ Get details for an Entity as RDF
    """
    query = '''
        DESCRIBE <'''+ entity_uri + '''>
    '''
    return sparqlqueries.query_turtle(query)


def get_entity_details_svg(entity_dict):
    """ Construct the SVG code for an Entity
    """
    # Draw Entity
    eLabel = entity_dict.get('l', 'uri')
    script = '''
            var eLabel = "''' + eLabel + '''";
            var entity = addEntity(380, 255, eLabel, "");
    '''

    # Draw value if it has one
    if entity_dict.get('v'):
        script += '''
            var value = addValue(305, 400, "''' + entity_dict.get('v') + '''");
            addLink(entity, value, "prov:value", RIGHT);
        '''

    # Draw Person (if one exists)
    if entity_dict.get('wat'):
        agent_uri = entity_dict.get('wat')
        agent_uri_encoded = urllib.quote(agent_uri)
        agent_name = entity_dict.get('wat_name', '')
        if agent_name == '':
            agent_name = agent_uri.split('#')
            if len(agent_name) < 2:
                agent_name = agent_uri.split('/')
            agent_name = agent_name[-1]
            script += '''
                var agentLabel = "''' + agent_name + '''";
                var agentUri = "''' + settings.WEB_SUBFOLDER + "/id/agent/?uri=" + agent_uri_encoded + '''";
                var agent = addAgent(305, 5, agentLabel, agentUri);
                addLink(entity, agent, "prov:wasAttributedTo", RIGHT);
            '''
    return [True, script]


def get_entity_activity_wgb_svg(entity_uri):
    """ Get all prov:wasGeneratedBy Activities for an Entity
    """
    script = ''
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?a ?t
        WHERE {
            GRAPH ?g {
                ?a prov:generated <''' + entity_uri + '''> .
                ?a rdfs:label ?t .
            }
        }
    '''
    entity_results = sparqlqueries.query(query)
    if entity_results and 'results' in entity_results:
        wgb = entity_results['results']['bindings']
        if len(wgb) == 1:
            if wgb[0].get('t'):
                title = wgb[0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wgb[0]['a']['value'])
            script += '''
                var aLabel = "''' + title + '''";
                var aUri = "''' + settings.WEB_SUBFOLDER + "/id/activity/?uri=" + uri_encoded + '''";
                var activityWGB = addActivity(5, 205, aLabel, aUri);
                addLink(entity, activityWGB, "prov:wasGeneratedBy", TOP);
            '''
        else:
            pass
    return script


def get_entity_activity_used_svg(entity_uri):
    """ Construct SVG code for the prov:used Activities of an Entity
    """
    script = ''
    query = '''
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?a ?t
WHERE {
    GRAPH ?g {
        ?a prov:used <''' + entity_uri + '''> .
        ?a rdfs:label ?t .
    }
}
    '''
    entity_result = sparqlqueries.query(query)
    if entity_result and 'results' in entity_result:
        used = entity_result['results']['bindings']
        if len(used) == 1:
            if used[0].get('t'):
                title = used[0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(used[0]['a']['value'])
            script = '''
                var aLabel = "''' + title + '''";
                var aUri = "''' + settings.WEB_SUBFOLDER + "/id/activity/?uri=" + uri_encoded + '''";
                var activityUsed = addActivity(555, 205, aLabel, aUri);
                addLink(activityUsed, entity, "prov:used", TOP);
            '''
        # TODO: Test, no current Entities have multiple prov:used Activities
        elif len(used) > 1:
            # TODO: Check query
            query_encoded = urllib.quote(query)
            script += '''
                activityUsed1 = addActivity(555, 215, "", "");
                activityUsed2 = addActivity(550, 210, "", "");
                activityUsedN = addActivity(545, 205, "Multiple Activities, click to search", "''' + settings.WEB_SUBFOLDER + "/function/sparql/?query=" + query_encoded + '''");
                addLink(activityUsedN, entity, "prov:used", TOP);
            '''
        else:
            # do nothing as no Activities found
            pass
    else:
        # we have a fault
        script += '''
            var activityFault = addActivity(550, 205, "There is a fault with retrieving Activities that may have used this Entity", "");
        '''
    return script


# TODO: Untested
def get_entity_entity_wdf_svg(entity_uri):
    """ Get the prov:wasDerivedFrom Entities of an Entity
    """
    # XXX Could add the extra WDF to the original Entity query and not have to
    # re-query
    script = ''
    query = '''
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?e ?t
WHERE {
    GRAPH ?g {
        { <''' + entity_uri + '''> a prov:Entity . }
        UNION
        { <''' + entity_uri + '''> a prov:Plan . }
        <''' + entity_uri + '''> prov:wasDerivedFrom ?e .
        ?e rdfs:label ?t .
    }
}
    '''
    entity_results = sparqlqueries.query(query)

    if entity_results and 'results' in entity_results:
        wdf = entity_results['results']['bindings']
        if len(wdf) == 1:
            if wdf[0].get('t'):
                title = wdf[0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wdf[0]['e']['value'])
            script += '''
                var entityWDF = addEntity(355, 440, "''' + title + '''", "''' + settings.WEB_SUBFOLDER + "/id/entity/?uri=" + uri_encoded + '''");
                drawLink(entityWDF, entity, "prov:wasDerivedFrom", TOP);
            '''
        elif len(wdf) > 1:
            # TODO: Check query
            query_encoded = urllib.quote(query)
            script += '''
                var entityWDF1 = addEntity(355, 440, "", "");
                var entityWDF2 = addEntity(350, 435, "", "");
                var entityWDFN = addEntity(345, 430, "Multiple Entities, click here to search", "''' + settings.WEB_SUBFOLDER + "function/sparql/?query=" + query_encoded + '''");
                drawLink(entityWDFN, entity, "prov:wasDerivedFrom", TOP);
            '''
        else:
            # do nothing as no Activities found
            pass
    else:
        # we have a fault
        script += '''
            var entityFaultText = addEntity(350, 440, "There is a fault with retrieving Activities that may have used this Entity", "");
        '''
    return script
