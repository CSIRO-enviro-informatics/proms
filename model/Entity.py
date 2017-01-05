from flask import Response, render_template
from rdflib import Graph
import urllib
import settings
import database
from modules.ldapi import LDAPI


class EntityRenderer:
    def __init__(self, g, uri):
        # load Entity data from given graph
        self.g = g
        self.uri = uri

    def get_graph(self):
        """
        Returns the graph of an object in the graph database

        :param uri: the URI of something in the graph database
        :return: an RDF Graph
        """
        uri = self.uri
        if uri is not None:
            r = sparqlqueries.query_turtle(q)
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

    def render_view_format(self, view, mimetype):
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
                    'class_entity.html',
                    entity=self.get_details()
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
                        rdfs:label ?label .
                    OPTIONAL {
                        ?a_u prov:used <%(uri)s> .
                    }
                    OPTIONAL {
                        <%(uri)s> prov:value ?v .
                    }
                    OPTIONAL {
                        ?a_g prov:generated <%(uri)s> .
                    }
                    OPTIONAL {
                        <%(uri)s> prov:generatedAtTime ?gat .
                    }
                    OPTIONAL {
                        <%(uri)s> prov:wasAttributedTo ?wat .
                    }
                }
            }
        ''' % {'uri': self.uri}
        res = database.query(query)
        return res
    
    def get_details(self):
        """ Get details for an Entity (dict)"""
        entity_details = self._get_details_query()
        ret = {}
        if entity_details and 'results' in entity_details:
            if len(entity_details['results']['bindings']) > 0:
                index = 0
                ret = entity_details['results']['bindings'][index]
                ret['uri'] = self.uri
                ret['label'] = ret['label']['value']
                if 'v' in ret:
                    ret['v'] = ret['v']['value']
                if 'a_u' in ret:
                    ret['a_u'] = ret['a_u']['value']
                if 'a_g' in ret:
                    ret['a_g'] = ret['a_g']['value']
                if 'gat' in ret:
                    ret['gat'] = ret['gat']['value']
                if 'wat' in ret:
                    ret['wat'] = ret['wat']['value']
                svg_script = self.get_details_svg(ret)
                if svg_script[0]:
                    e_script = svg_script[1]
                    e_script += self.get_activity_wgb_svg()
                    e_script += self.get_activity_used_svg()
                    e_script += self.get_wdf_svg()
                    ret['e_script'] = e_script
        return ret

    def get_entity_rdf(self):
        """ Get details for an Entity as RDF"""
        query = 'DESCRIBE <%(uri)s>' % {'uri': self.uri}
        return database.query_turtle(query)

    def get_details_svg(self, entity_dict):
        """ Construct the SVG code for an Entity
        """
        # Draw Entity
        eLabel = entity_dict.get('label', 'uri')
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
                        var agentUri = "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + agent_uri_encoded + '''";
                        var agent = addAgent(305, 5, agentLabel, agentUri);
                        addLink(entity, agent, "prov:wasAttributedTo", RIGHT);
                    '''
        return [True, script]

    def get_activity_wgb_svg(self):
        """ Get all prov:wasGeneratedBy Activities for an Entity
        """
        script = ''
        query = '''
                PREFIX prov: <http://www.w3.org/ns/prov#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT *
                WHERE {
                    GRAPH ?g {
                        ?a prov:generated <%(uri)s> .
                        ?a rdfs:label ?label .
                    }
                }
                ''' % {'uri': self.uri}
        entity_results = database.query(query)
        if entity_results and 'results' in entity_results:
            wgb = entity_results['results']['bindings']
            if len(wgb) == 1:
                if wgb[0].get('label'):
                    label = wgb[0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(wgb[0]['a']['value'])
                script += '''
                        var aLabel = "''' + label + '''";
                        var aUri = "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + uri_encoded + '''";
                        var activityWGB = addActivity(5, 205, aLabel, aUri);
                        addLink(entity, activityWGB, "prov:wasGeneratedBy", TOP);
                    '''
            else:
                pass
        return script

    def get_activity_used_svg(self):
        """ Construct SVG code for the prov:used Activities of an Entity
        """
        script = ''
        query = '''
                PREFIX prov: <http://www.w3.org/ns/prov#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT *
                WHERE {
                    GRAPH ?g {
                        ?a prov:used <%(uri)s> .
                        ?a rdfs:label ?label .
                    }
                }
                ''' % {'uri': self.uri}
        entity_result = database.query(query)
        if entity_result and 'results' in entity_result:
            used = entity_result['results']['bindings']
            if len(used) == 1:
                if used[0].get('label'):
                    label = used[0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(used[0]['a']['value'])
                script = '''
                        var aLabel = "''' + label + '''";
                        var aUri = "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + uri_encoded + '''";
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

    def get_wdf_svg(self):
        """ Get the prov:wasDerivedFrom Entities of an Entity
        """
        # XXX Could add the extra WDF to the original Entity query and not have to
        # re-query
        script = ''
        query = '''
                PREFIX prov: <http://www.w3.org/ns/prov#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT DISTINCT ?e ?label
                WHERE {
                    GRAPH ?g {
                        { <%(uri)s> a prov:Entity . }
                        UNION
                        { <%(uri)s> a prov:Plan . }
                        <%(uri)s> prov:wasDerivedFrom ?e .
                        ?e rdfs:label ?label .
                    }
                }
                ''' % {'uri': self.uri}
        entity_results = database.query(query)

        if entity_results and 'results' in entity_results:
            wdf = entity_results['results']['bindings']
            if len(wdf) == 1:
                if wdf[0].get('label'):
                    label = wdf[0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(wdf[0]['e']['value'])
                script += '''
                        var entityWDF = addEntity(355, 440, "''' + label + '''", "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + uri_encoded + '''");
                        drawLink(entityWDF, entity, "prov:wasDerivedFrom", TOP);
                    '''
            elif len(wdf) > 1:
                # TODO: Check query
                query_encoded = urllib.quote(query)
                script += '''
                        var entityWDF1 = addEntity(355, 440, "", "");
                        var entityWDF2 = addEntity(350, 435, "", "");
                        var entityWDFN = addEntity(345, 430, "Multiple Entities, click here to search", "''' + settings.WEB_SUBFOLDER + "/function/sparql/?query=" + query_encoded + '''");
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
