from .renderer import Renderer
from flask import Response, render_template
import database
import urllib
from modules.ldapi import LDAPI
from rdflib import Graph, URIRef, Literal, Namespace


class AgentRenderer(Renderer):
    def __init__(self, uri, endpoints):
        Renderer.__init__(self, uri, endpoints)

        self.uri_encoded = urllib.quote_plus(uri)
        self.label = None
        self.aobo = None
        self.aobo_label = None
        self.script = None

    def render(self, view, mimetype):
        if view == 'neighbours':
            if mimetype in LDAPI.get_rdf_mimetypes_list():
                return self._neighbours_rdf(mimetype)
            elif mimetype == 'text/html':
                self._get_details()
                return self._neighbours_html()
        elif view == 'prov':
            if mimetype in LDAPI.get_rdf_mimetypes_list():
                return Response(
                    self._prov_rdf().serialize(format=LDAPI.get_rdf_parser_for_mimetype(mimetype)),
                    status=200,
                    mimetype=mimetype
                )
            elif mimetype == 'text/html':
                self._get_details()
                return self._prov_html()

    def _neighbours_rdf(self, mimetype):
        query = '''
                  SELECT * WHERE {
                     <%(uri)s>  ?p ?o .
                  }
          ''' % {'uri': self.uri}
        g = Graph()
        g.bind('prov', Namespace('http://www.w3.org/ns/prov#'))
        for r in database.query(query)['results']['bindings']:
            if r['o']['type'] == 'literal':
                g.add((URIRef(self.uri), URIRef(r['p']['value']), Literal(r['o']['value'])))
            else:
                g.add((URIRef(self.uri), URIRef(r['p']['value']), URIRef(r['o']['value'])))

        query2 = '''
                  SELECT * WHERE {
                     ?s ?p <%(uri)s> .
                  }
          ''' % {'uri': self.uri}
        for r in database.query(query2)['results']['bindings']:
            g.add((URIRef(r['s']['value']), URIRef(r['p']['value']), URIRef(self.uri)))

        return Response(
            g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(mimetype)),
            status=200,
            mimetype=mimetype
        )

    def _neighbours_html(self):
        """Returns a simple dict of Activity properties for use by a Jinja template"""
        self._make_svg_script()

        ret = {
            'uri': self.uri,
            'uri_encoded': self.uri_encoded,
            'label': self.label,
            'aobo': self.aobo,
            'aobo_label': self.aobo_label,
            'script': self.script
        }

        return render_template(
            'class_activity.html',
            activity=ret
        )

    def _prov_rdf(self):
        query = '''
                 SELECT * WHERE {
                    <%(uri)s>  ?p ?o .
                 }
         ''' % {'uri': self.uri}
        g = Graph()
        g.bind('prov', Namespace('http://www.w3.org/ns/prov#'))
        for r in database.query(query)['results']['bindings']:
            if r['o']['type'] == 'literal':
                g.add((URIRef(self.uri), URIRef(r['p']['value']), Literal(r['o']['value'])))
            else:
                g.add((URIRef(self.uri), URIRef(r['p']['value']), URIRef(r['o']['value'])))

        query2 = '''
                 SELECT * WHERE {
                    ?s ?p <%(uri)s> .
                 }
         ''' % {'uri': self.uri}
        for r in database.query(query2)['results']['bindings']:
            g.add((URIRef(r['s']['value']), URIRef(r['p']['value']), URIRef(self.uri)))

        return g

    def _prov_html(self):
        """Returns a simple dict of Entity properties for use by a Jinja template"""
        ret = {
            'uri': self.uri,
            'uri_encoded': self.uri_encoded,
            'label': self.label,
            'aobo': self.aobo,
            'aobo_label': self.aobo_label
        }

        prov_data = self._prov_rdf().serialize(format='turtle')

        return render_template(
            'class_entity_prov.html',
            agent=ret,
            prov_data=prov_data
        )

    def _get_details(self):
        """ Get the details for an Agent from an RDF triplestore"""
        # formulate the query
        query = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE { GRAPH ?g {
                <%(uri)s>
                    a prov:Agent ;
                    rdfs:label ?label .
                OPTIONAL {
                    <%(uri)s> prov:actedOnBehalfOf ?aobo .
                    ?aobo rdfs:label ?aobo_label
                }
              }
            }
            ''' % {'uri': self.uri}

        # run the query
        agent_details = database.query(query)

        # extract results into instance vars
        if 'results' in agent_details:
            if len(agent_details['results']['bindings']) > 0:
                ret = agent_details['results']['bindings'][0]
                self.label = ret['label']['value']
                if 'aobo' in ret:
                    self.aobo = ret['aobo']['value']
                    self.aobo_label = ret['aobo_label']['value']

    def _make_svg_script(self):
        """ Construct the SVG code for an Agent's Neighbours view"""
        self.script = '''
            var aLabel = "%(label)s";
            var agent = addAgent(310, 200, aLabel, "");
        ''' % {'label': self.label if self.label is not None else 'uri'}

        self._get_aobo()

    def _get_aobo(self):
        if self.aobo is not None:
            aobo_uri_encoded = urllib.quote(self.aobo)
            aobo_label = self.aobo_label if self.aobo_label is not None else 'uri'

            self.script += '''
                var agentAOBO = addAgent(310, 5, "%(aobo_label)s", "%(instance_endpoint)s?_uri=%(aobo_uri_encoded)s");
                addLink(agent, agentAOBO, "prov:actedOnBehalfOf", LEFT);
            ''' % {
                'aobo_label': aobo_label,
                'instance_endpoint': self.endpoints['instance'],
                'aobo_uri_encoded': aobo_uri_encoded
            }

    def get_agent_was_attributed_to_svg(self):
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
            if len(wat['bindings']) > 0:
                if wat['bindings'][0].get('label'):
                    label = wat['bindings'][0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(wat['bindings'][0]['e']['value'])
                script += '''
                    entityLabel = "%(label)s";
                    entityUri = "%(instance_endpoint)s?_uri=%(uri_encoded)s";
                    var entityWAT = addEntity(385, 430, entityLabel, entityUri);
                    addLink(entity, entityWAT, "prov:wasAttributedTo", RIGHT);
                ''' % {
                    'label': label,
                    'instance_endpoint': self.endpoints['instance'],
                    'uri_encoded': uri_encoded
                }
            elif len(wat['bindings']) > 1:
                query_encoded = urllib.quote(query)
                script += '''
                    var entityWAT1 = addEntity(395, 440, "", "");
                    var entityWAT2 = addEntity(390, 435, "", "");
                    var entityWATN = addEntity(385, 430, "Multiple Entities, click here to search", "%(sparql_endpoint)s?query=%(query_encoded)s");
                    addLink(agent, entityWATN, "prov:wasAttributedTo", RIGHT);
                ''' % {
                    'sparql_endpoint': self.endpoints['sparql'],
                    'query_encoded': query_encoded
                }
            else:
                # do nothing as no Activities found
                pass
        else:
            # we have a fault
            script += '''
                var addEntity(550, 200, "There is a fault with retrieving Activities that may have used this Entity", "");
            '''
        return script

    def get_agent_was_associated_with_svg(self):
        """ Construct the SVG code for the prov:wasAssociatedWith Activities of an Agent"""
        script = ''
        query = '''
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX prov: <http://www.w3.org/ns/prov#>
                SELECT DISTINCT ?a ?label
                WHERE {
                    GRAPH ?g {
                        { ?a a prov:Activity . }
                        ?waw prov:wasAssociatedWith <%(uri)s> ;
                        OPTIONAL { ?waw rdfs:label ?waw_label . }
                    }
                }
            ''' % {'uri': self.uri}
        activity_results = database.query(query)

        if activity_results and 'results' in activity_results:
            waw = activity_results['results']
            if len(waw['bindings']) > 0:
                if waw['bindings'][0].get('waw_label'):
                    waw_label = waw['bindings'][0]['waw_label']['value']
                else:
                    waw_label = 'uri'
                waw_uri_encoded = urllib.quote(waw['bindings'][0]['waw']['value'])
                script += '''
                    activityLabel = "%(waw_label)s";
                    activityUri = "%(instance_endpoint)s?_uri=%(waw_uri_encoded)s";
                    var activityWAW = addActivity(5, 200, activityLabel, activityUri);
                    addLink(agent, activityWAW, "prov:wasAssociatedWith", TOP);
                ''' % {
                    'waw_label': waw_label,
                    'instance_endpoint': self.endpoints['instance'],
                    'waw_uri_encoded': waw_uri_encoded
                }
            elif len(waw['bindings']) > 1:
                query_encoded = urllib.quote(query)
                script += '''
                    var activityWAW1 = addActivity(15, 210, "", "");
                    var activityWAW2 = addActivity(10, 205, "", "");
                    var activityWAWN = addActivity(5, 200, "Multiple Activities, click here to search", "%(sparql_endpoint)s?query=%(query_encoded)s'");
                    addLink(agent, activityWAWN, "prov:wasAssociatedWith", TOP);
                ''' % {
                    'sparql_endpoint': self.endpoints['sparql'],
                    'query_encoded': query_encoded
                }
            else:
                # do nothing as no Activities found
                pass
        else:
            # we have a fault
            script += '''
                var activityUsedFaultText = addActivity(5, 200, "There is a fault with retrieving Activities that may be associated with this Person", "");
            '''

        self.script += script

    def _export_for_html_template(self):
        """Returns a simple dict of Agent properties for use by a Jinja template"""
        ret = {
            'uri': self.uri,
            'uri_encoded': self.uri_encoded,
            'label': self.label
        }

        if self.script is not None:
            ret['script'] = self.script

        return ret