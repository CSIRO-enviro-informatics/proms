from flask import Response, render_template
import settings
import urllib
import database
from modules.ldapi import LDAPI


class ActivityRenderer:
    def __init__(self, g, uri):
        # load Entity data from given graph
        self.g = g
        self.uri = uri

    def render_view_format(self, view, mimetype):
        """
        Renders a model and format of an Activity

        No validation is needed as the model and format for an Activity are pre-validated before this class is
        instantiated
        :param view: An allowed model model of an Activity
        :param mimetype: An allowed format of an Activity
        :return: A Flask Response object
        """
        if view == 'neighbours':
            # no work to be done as we have already loaded the triples
            if mimetype in LDAPI.get_rdf_mimetypes_list():
                return Response(
                    self.g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(mimetype)),
                    status=200,
                    mimetype=mimetype
                )
            elif mimetype == 'text/html':
                return render_template(
                    'class_activity.html',
                    activity=self.get_details()
                )

    def _get_details_query(self):
        """ Get details for an Activity
        """
        query = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE {
                GRAPH ?g {
                    <%(uri)s>
                        rdfs:label ?label ;
                        prov:startedAtTime ?sat ;
                        prov:endedAtTime ?eat .
                    OPTIONAL {
                        <%(uri)s> prov:wasAssociatedWith ?waw .
                    }
                }
            }
        ''' % {'uri': self.uri}
        res = database.query(query)
        return res

    def get_activity_rdf(self):
        """ Get the details of an Activity as RDF"""
        query = 'DESCRIBE <%(uri)s>' % {'uri': self.uri}
        return database.query_turtle(query)

    def get_details(self):
        """ Get the details of an Activity (dict)
        """
        activity_details = self._get_details_query()
        ret = {}
        if activity_details and 'results' in activity_details:
            if len(activity_details['results']['bindings']) > 0:
                index = 0
                ret = activity_details['results']['bindings'][index]
                ret['uri'] = self.uri
                ret['label'] = ret['label']['value']
                if 'sat' in ret:
                    ret['sat'] = ret['sat']['value']
                if 'eat' in ret:
                    ret['eat'] = ret['eat']['value']
                if 'waw' in ret:
                    ret['waw'] = ret['waw']['value']
                # if 'waw_name' in ret:
                #     ret['waw_name'] = ret['waw_name']['value']
                if 'r' in ret:
                    ret['r'] = urllib.quote(ret['r']['value'])
                    ret['r_u'] = ret['r']['value']
                if 'rt' in ret:
                    ret['rt'] = ret['rt']['value']
                svg_script = self.get_details_svg(ret)
                if svg_script[0]:
                    a_script = svg_script[1]
                    a_script += self.get_used_entities_svg()
                    a_script += self.get_generated_entities_svg()
                    a_script += self.get_was_informed_by()
                    ret['a_script'] = a_script
        return ret

    def get_details_svg(self, activity_dict):
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
                var agentUri = "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + agent_uri_encoded + '''";
                var agent = addAgent(275, 5, agentName, agentUri);
                addLink(activity, agent, "prov:wasAssociatedWith", RIGHT);
            '''
        return [True, script]

    def get_used_entities_svg(self):
        """ Construct the SVG code for the prov:used Entities of an Activity
        """
        script = ''
        query = '''
                PREFIX prov: <http://www.w3.org/ns/prov#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT *
                WHERE {
                    GRAPH ?g {
                        <%(uri)s> prov:used ?u .
                        OPTIONAL {?u rdfs:label ?label .}
                    }
                }
            ''' % {'uri': self.uri}
        print query
        activity_results = database.query(query)
        if activity_results and 'results' in activity_results:
            used = activity_results['results']
            if len(used['bindings']) > 0:
                if used['bindings'][0].get('label'):
                    label = used['bindings'][0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(used['bindings'][0]['u']['value'])
                script += '''
                    var entityUsed1 = addEntity(105, 250, "''' + label + '''", "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + uri_encoded + '''");
                    addLink(activity, entityUsed1, "prov:used", TOP);
                '''
                # TODO: Loop this if 1-3 Entities
                if len(used['bindings']) > 1:
                    if used['bindings'][1].get('label'):
                        label = used['bindings'][1]['label']['value']
                    else:
                        label = 'uri'
                    uri_encoded = urllib.quote(used['bindings'][1]['u']['value'])

                    script += '''
                        var entityUsed2 = addEntity(105, 100, "''' + label + '''", "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + uri_encoded + '''");
                        addLink(activity, entityUsed2, "prov:used", TOP);
                    '''
                    if len(used['bindings']) == 3:
                        if used['bindings'][2].get('label'):
                            label = used['bindings'][2]['label']['value']
                        else:
                            label = 'uri'
                        uri_encoded = urllib.quote(used['bindings'][2]['u']['value'])

                        script += '''
                            var entityUsed3 = addEntity(105, 400, "''' + label + '''", "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + uri_encoded + '''");
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
            # we have a fault
            script += '''
                var entityUsedFaultText = addEntity(1, 200, "There is a fault with retrieving Entities that may have been used by this Activity", "");
            '''
        return script

    def get_generated_entities_svg(self):
        """ Construct the SVG code for the prov:generated Entities of an Activity
        """
        script = ''
        query = '''
                PREFIX prov: <http://www.w3.org/ns/prov#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT *
                WHERE {
                    GRAPH ?g {
                        { <%(uri)s> prov:generated ?u . }
                        UNION
                        { ?u prov:wasGeneratedBy <%(uri)s> .}
                        OPTIONAL {?u rdfs:label ?label .}
                    }
                }
                ''' % {'uri': self.uri}

        activity_results = database.query(query)
        if activity_results and 'results' in activity_results:
            gen = activity_results['results']
            if len(gen['bindings']) > 0:
                if gen['bindings'][0].get('label'):
                    label = gen['bindings'][0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(gen['bindings'][0]['u']['value'])
                script += '''
                    var entityGen1 = addEntity(605, 250, "''' + label + '''", "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + uri_encoded + '''");
                    addLink(activity, entityGen1, "prov:generated", TOP);
                '''
                # Could make a loop to 3
                if len(gen['bindings']) > 1:
                    if gen['bindings'][1].get('label'):
                        label = gen['bindings'][1]['label']['value']
                    else:
                        label = 'uri'
                    uri_encoded = urllib.quote(gen['bindings'][1]['u']['value'])

                    script += '''
                        var entityGen2 = addEntity(605, 100, "''' + label + '''", "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + uri_encoded + '''");
                        addLink(activity, entityGen2, "prov:generated", TOP);
                    '''
                    if len(gen['bindings']) == 3:
                        if gen['bindings'][2].get('label'):
                            label = gen['bindings'][2]['label']['value']
                        else:
                            label = 'uri'
                        uri_encoded = urllib.quote(gen['bindings'][2]['u']['value'])

                        script += '''
                            var entityGen3 = addEntity(605, 400, "''' + label + '''", "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + uri_encoded + '''");
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
    def get_was_informed_by(self):
        """ Construct the SVG code for the prov:wasInformedBy Activities of an Activity
        """
        script = ''
        query = '''
                PREFIX prov: <http://www.w3.org/ns/prov#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT *
                WHERE {
                    GRAPH ?g {
                        <%(uri)s> a prov:Activity .
                        <%(uri)s> prov:wasInformedBy ?wif .
                        OPTIONAL { ?wif rdfs:label ?label . }
                    }
                }
                ''' % {'uri': self.uri}
        activity_results = database.query(query)

        if activity_results and 'results' in activity_results:
            wif = activity_results['results']
            if len(wif['bindings']) == 1:
                if wif['bindings'][0].get('label'):
                    label = wif['bindings'][0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(wif['bindings'][0]['wif']['value'])
                script += '''
                    var activityWIB = addActivity(275, 399, "''' + label + '''", "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + uri_encoded + '''");
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