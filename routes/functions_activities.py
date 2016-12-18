import urllib
import functions_sparqldb
import settings


def get_activities_dict():
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
    activities = functions_sparqldb.query(query)
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
    return functions_sparqldb.query(query)


def get_activity_dict(activity_uri):
    """ Get the details of an Activity (dict)
    """
    activity_detail = get_activity(activity_uri)
    ret = {}
    if activity_detail and 'results' in activity_detail:
        if len(activity_detail['results']['bindings']) > 0:
            ret['uri'] = activity_uri
            ret['uri_html'] = urllib.quote(activity_uri)
            ret['l'] = activity_detail['results']['bindings'][0]['l']['value']
            if 't' in activity_detail['results']['bindings'][0]:
                ret['t'] = activity_detail['results']['bindings'][0]['t']['value']
            if 'sat' in activity_detail['results']['bindings'][0]:
                ret['sat'] = activity_detail['results']['bindings'][0]['sat']['value']
            if 'eat' in activity_detail['results']['bindings'][0]:
                ret['eat'] = activity_detail['results']['bindings'][0]['eat']['value']
            if 'waw' in activity_detail['results']['bindings'][0]:
                ret['waw'] = activity_detail['results']['bindings'][0]['waw']['value']
            if 'waw_name' in activity_detail['results']['bindings'][0]:
                ret['waw_name'] = activity_detail['results']['bindings'][0]['waw_name']['value']
            if 'r' in activity_detail['results']['bindings'][0]:
                ret['r'] = urllib.quote(activity_detail['results']['bindings'][0]['r']['value'])
                ret['r_u'] = activity_detail['results']['bindings'][0]['r']['value']
            if 'rt' in activity_detail['results']['bindings'][0]:
                ret['rt'] = activity_detail['results']['bindings'][0]['rt']['value']
            svg_script = get_activity_details_svg(ret)
            if svg_script[0]:
                a_script = svg_script[1]
                a_script += get_activity_used_entities_svg(activity_uri)
                a_script += get_activity_generated_entities_svg(activity_uri)
                a_script += get_activity_was_informed_by(activity_uri)
                ret['a_script'] = a_script
    return ret


def get_activity_rdf(activity_uri):
    """ Get the details of an Activity as RDF
    """
    query = '''
        DESCRIBE <''' + activity_uri + '''>
    '''
    return functions_sparqldb.query_turtle(query)


def get_activity_details_svg(activity_dict):
    """ Construct the SVG code for an Activity
    """
    aLabel = activity_dict.get('l', 'uri')
    script = '''
            var aLabel = "''' + aLabel + '''";
            var activity = addActivity(275, 200, aLabel, "");
    '''
    # print its Person, if it has one
    if activity_dict.get('waw'):
        agent_uri = activity_dict.get('waw', '')
        agent_uri_encoded = urllib.quote(agent_uri)
        if activity_dict.get('waw_name'):
            agent_name = activity_dict.get('waw_name')
        else:
            agent_name = agent_uri.split('#')
            if len(agent_name) < 2:
                agent_name = agent_uri.split('/')
            agent_name = agent_name[-1]
        script += '''
            var agentName = "''' + agent_name + '''";
            var agentUri = "''' + settings.WEB_SUBFOLDER + "/id/agent/?uri=" + agent_uri_encoded + '''";
            var agent = addAgent(275, 5, agentName, agentUri);
            addLink(activity, agent, "prov:wasAssociatedWith", RIGHT);
        '''
    return [True, script]


def get_activity_used_entities_svg(activity_uri):
    """ Construct the SVG code for the prov:used Entities of an Activity
    """
    script = ''
    query = '''
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT *
WHERE {
    GRAPH ?g {
        <''' + activity_uri + '''> prov:used ?u .
        OPTIONAL {?u rdfs:label ?t .}
    }
}
    '''
    activity_results = functions_sparqldb.query(query)
    if activity_results and 'results' in activity_results:
        used = activity_results['results']
        if len(used['bindings']) > 0:
            if used['bindings'][0].get('t'):
                title = used['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(used['bindings'][0]['u']['value'])
            script += '''
                var entityUsed1 = addEntity(105, 250, "''' + title + '''", "''' + settings.WEB_SUBFOLDER + "/id/entity/?uri=" + uri_encoded + '''");
                addLink(activity, entityUsed1, "prov:used", TOP);
            '''
            # TODO: Loop this if 1-3 Entities
            if len(used['bindings']) > 1:
                if used['bindings'][1].get('t'):
                    title = used['bindings'][1]['t']['value']
                else:
                    title = 'uri'
                uri_encoded = urllib.quote(used['bindings'][1]['u']['value'])

                script += '''
                    var entityUsed2 = addEntity(105, 100, "''' + title + '''", "''' + settings.WEB_SUBFOLDER + "/id/entity/?uri=" + uri_encoded + '''");
                    addLink(activity, entityUsed2, "prov:used", TOP);
                '''
                if len(used['bindings']) == 3:
                    if used['bindings'][2].get('t'):
                        title = used['bindings'][2]['t']['value']
                    else:
                        title = 'uri'
                    uri_encoded = urllib.quote(used['bindings'][2]['u']['value'])

                    script += '''
                        var entityUsed3 = addEntity(105, 400, "''' + title + '''", "''' + settings.WEB_SUBFOLDER + "/id/entity/?uri=" + uri_encoded + '''");
                        addLink(activity, entityUsed3, "prov:used", RIGHT);
                    '''
                elif len(used['bindings']) > 3:
                    query_encoded = urllib.quote(query)
                    script = ''  # reset script
                    script += '''
                        var entityUsed1 = addEntity(105, 260, "", "");
                        var entityUsed2 = addEntity(100, 255, "", "");
                        var entityUsedN = addEntity(95, 250, "Multiple Entities, click here to search", "''' + settings.WEB_SUBFOLDER + "/function/sparql/?query=" + query_encoded + '''");
                        addLink(activity, entityUsedN, "prov:used", TOP);
                    '''
        else:
            # zero
            pass
    else:
        #we have a fault
        script += '''
            var entityUsedFaultText = addEntity(1, 200, "There is a fault with retrieving Entities that may have been used by this Activity", "");
        '''
    return script


def get_activity_generated_entities_svg(activity_uri):
    """ Construct the SVG code for the prov:generated Entities of an Activity
    """
    script = ''
    query = '''
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT *
WHERE {
    GRAPH ?g {
        { <''' + activity_uri + '''> prov:generated ?u . }
        UNION
        { ?u prov:wasGeneratedBy <''' + activity_uri + '''> .}
        OPTIONAL {?u rdfs:label ?t .}
    }
}
    '''

    activity_results = functions_sparqldb.query(query)
    if activity_results and 'results' in activity_results:
        gen = activity_results['results']
        if len(gen['bindings']) > 0:
            if gen['bindings'][0].get('t'):
                title = gen['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(gen['bindings'][0]['u']['value'])
            script += '''
                var entityGen1 = addEntity(605, 250, "''' + title + '''", "''' + settings.WEB_SUBFOLDER + "/id/entity/?uri=" + uri_encoded + '''");
                addLink(activity, entityGen1, "prov:generated", TOP);
            '''
            # Could make a loop to 3
            if len(gen['bindings']) > 1:
                if gen['bindings'][1].get('t'):
                    title = gen['bindings'][1]['t']['value']
                else:
                    title = 'uri'
                uri_encoded = urllib.quote(gen['bindings'][1]['u']['value'])

                script += '''
                    var entityGen2 = addEntity(605, 100, "''' + title + '''", "''' + settings.WEB_SUBFOLDER + "/id/entity/?uri=" + uri_encoded + '''");
                    addLink(activity, entityGen2, "prov:generated", TOP);
                '''
                if len(gen['bindings']) == 3:
                    if gen['bindings'][2].get('t'):
                        title = gen['bindings'][2]['t']['value']
                    else:
                        title = 'uri'
                    uri_encoded = urllib.quote(gen['bindings'][2]['u']['value'])

                    script += '''
                        var entityGen3 = addEntity(605, 400, "''' + title + '''", "''' + settings.WEB_SUBFOLDER + "/id/entity/?uri=" + uri_encoded + '''");
                        addLink(activity, entityGen3, "prov:generated", TOP);
                    '''
                elif len(gen['bindings']) > 3:
                    # TODO: Check query
                    query_encoded = urllib.quote(query)
                    script = ''  # reset script
                    script += '''
                        var entityGen1 = addEntity(615, 260, "", "");
                        var entityGen2 = addEntity(610, 255, "", "");
                        var entityGenN = addEntity(605, 250, "Multiple Entities, click here to search", "''' + settings.WEB_SUBFOLDER + "/function/sparql/?query=" + query_encoded + '''");
                        addLink(activity, entityGenN, "prov:generated", TOP);
                    '''
        else:
            # zero
            pass
    else:
        # we have a fault
        script += '''
            var entityGenFaultText = addEntity(349, 200, "There is a fault with retrieving Entities that may have been used by this Activity", "");
        '''
    return script


# TODO: Untested
def get_activity_was_informed_by(activity_uri):
    """ Construct the SVG code for the prov:wasInformedBy Activities of an Activity
    """
    script = ''
    query = '''
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT *
WHERE {
    GRAPH ?g {
        <''' + activity_uri + '''> a prov:Activity .
        <''' + activity_uri + '''> prov:wasInformedBy ?wif .
        OPTIONAL { ?wif rdfs:label ?t . }
    }
}
    '''
    activity_results = functions_sparqldb.query(query)

    if activity_results and 'results' in activity_results:
        wif = activity_results['results']
        if len(wif['bindings']) == 1:
            if wif['bindings'][0].get('t'):
                title = wif['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wif['bindings'][0]['wif']['value'])
            script += '''
                var activityWIB = addActivity(275, 399, "''' + title + '''", "''' + settings.WEB_SUBFOLDER + "/id/activity/?uri=" + uri_encoded + '''");
                addLink(activity, activityWIB, "prov:wasInformedBy", RIGHT);
            '''
        # TODO: Check query
        elif len(wif['bindings']) > 1:
            query_encoded = urllib.quote(query)
            script += '''
                var activityWIB1 = addActivity(275, 399, "", "");
                var activityWIB2 = addActivity(270, 394, "", "")
                var activityWIBN = addActivity(2650, 389, "Multiple Activities, click here to search", "''' + settings.WEB_SUBFOLDER + "/function/sparql/?query=" + query_encoded + '''");
                addLink(activity, activityWIBN, "prov:wasInformedBy", RIGHT);
            '''
        else:
            # do nothing as no Activities found
            pass
    else:
        # we have a fault
        script += '''
            var activityUsedFaultText = addActivity(550, 200, "There is a fault with retrieving Activities that may have used this Entity", "");
        '''
    return script
