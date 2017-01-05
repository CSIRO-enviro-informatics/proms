from flask import Response, render_template
import database.get_things
import settings
import urllib
from modules.ldapi import LDAPI


class AgentRenderer:
    def __init__(self, g, uri):
        # load Entity data from given graph
        self.g = g
        self.uri = uri

    def render_view_format(self, view, mimetype):
        """
        Renders a model and format of an Agent

        No validation is needed as the model and format for an Agent are pre-validated before this class is
        instantiated
        :param view: An allowed model model of an Agent
        :param mimetype: An allowed format of an Agent
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
                    'class_agent.html',
                    agent=self.get_details()
                )

    def get_details(self):
        """ Get an Agent from the provenance database"""

        query = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE { GRAPH ?g {
                <%(agent_uri)s>
                    a prov:Agent ;
                    rdfs:label ?label .
                OPTIONAL {
                    <%(agent_uri)s> prov:actedOnBehalfOf ?aobo .
                }
              }
            }
            ''' % {'agent_uri': self.uri}
        # agent = None
        # for row in database.query(q)['results']['bindings']:
        #     agent = {
        #         'uri': self.uri,
        #         'label': row['label']['value']
        #     }

        agent_details = database.query(query)
        ret = {}
        if 'results' in agent_details:
            if len(agent_details['results']['bindings']) > 0:
                ret['label'] = agent_details['results']['bindings'][0]['label']['value']
                if agent_details['results']['bindings'][0].get('aobo') is not None:
                    ret['aobo'] = agent_details['results']['bindings'][0]['aobo']['value']
                ret['uri'] = self.uri

        svg_script = self.get_svg(ret)
        if svg_script[0]:
            ret['a_script'] = svg_script[1]
        return ret

    def get_svg(self, agent_dict):
        """ Construct the SVG code for an Person
        """
        a_uri = agent_dict.get('uri')
        if agent_dict.get('label'):
            a_label = agent_dict.get('label')
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

        # print actedOnBehalfOf, if it has one
        if agent_dict.get('aobo'):
            agent_uri = agent_dict.get('aobo')
            agent_uri_encoded = urllib.quote(agent_uri)
            agent_name = agent_uri
            agent_name = agent_name.split('#')
            if len(agent_name) < 2:
                agent_name = agent_uri.split('/')
            agent_name = agent_name[-1]
            script += '''
                var agentAOBO = addAgent(310, 5, "''' + agent_name + '''", "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + agent_uri_encoded + '''");
                addLink(agent, agentAOBO, "prov:actedOnBehalfOf", LEFT);
            '''
        return [True, script]

    # TODO: test
    def get_agent_was_attributed_to_svg(self, agent_uri):
        """ Construct the SVG code for the prov:wasAttributedTo Entities of an Person
        """
        script = ''
        query = '''
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX prov: <http://www.w3.org/ns/prov#>
                SELECT DISTINCT ?e ?label
                WHERE {
                    GRAPH ?g {
                        { ?e a prov:Entity .}
                        UNION
                        { ?e a prov:Plan .}
                        ?e prov:wasAttributedTo <%(agent_uri)s> ;
                        OPTIONAL { ?e rdfs:label ?label . }
                    }
                }
                ''' % {'agent_uri': self.uri}
        entity_results = database.query(query)

        if entity_results and 'results' in entity_results:
            wat = entity_results['results']
            if len(wat['bindings']) == 1:
                if wat['bindings'][0].get('label'):
                    label = wat['bindings'][0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(wat['bindings'][0]['e']['value'])
                script += '''
                    entityLabel = "''' + label + '''";
                    entityUri = "''' + settings.WEB_SUBFOLDER + '''/instance?_uri=''' + uri_encoded + '''";
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

    # TODO: test
    def get_agent_was_associated_with_svg(self, agent_uri):
        """ Construct the SVG code for the prov:wasAssociatedWith Activities of an Person
        """
        script = ''
        query = '''
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX prov: <http://www.w3.org/ns/prov#>
                SELECT DISTINCT ?a ?label
                WHERE {
                    GRAPH ?g {
                        { ?a a prov:Activity . }
                        ?a prov:wasAssociatedWith <%(agent_uri)s> ;
                        OPTIONAL { ?a rdfs:label ?label . }
                    }
                }
            ''' % {'agent_uri': self.uri}
        activity_results = database.query(query)

        if activity_results and 'results' in activity_results:
            waw = activity_results['results']
            if len(waw['bindings']) == 1:
                if waw['bindings'][0].get('label'):
                    label = waw['bindings'][0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(waw['bindings'][0]['a']['value'])
                script += '''
                    activityLabel = "''' + label + '''";
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

