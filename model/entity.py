from .renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
import urllib
import _database
from modules.ldapi import LDAPI


class EntityRenderer(Renderer):
    def __init__(self, uri, endpoints):
        Renderer.__init__(self, uri, endpoints)

        self.uri_encoded = urllib.quote_plus(uri)
        self.label = None
        self.value = None
        self.script = None

        self.g = None
        self.js = None

    def render(self, view, mimetype):
        if view == 'neighbours':
            # no work to be done as we have already loaded the triples
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
            # TODO: pre-render the viz.js image and serve static image
            # elif mimetype == 'image/svg':
            #     return Response(
            #
            #     )
            elif mimetype == 'text/html':
                self._get_details()
                return self._prov_html()

    # TODO: RDF neighbours view broken: only showing one Activity when there are many
    def _neighbours_rdf(self, mimetype):
        query = '''
                 SELECT * WHERE {
                    <%(uri)s>  ?p ?o .
                 }
         ''' % {'uri': self.uri}
        g = Graph()
        g.bind('prov', Namespace('http://www.w3.org/ns/prov#'))
        for r in _database.query(query)['results']['bindings']:
            if r['o']['type'] == 'literal':
                g.add((URIRef(self.uri), URIRef(r['p']['value']), Literal(r['o']['value'])))
            else:
                g.add((URIRef(self.uri), URIRef(r['p']['value']), URIRef(r['o']['value'])))

        query2 = '''
                 SELECT * WHERE {
                    ?s ?p <%(uri)s> .
                 }
         ''' % {'uri': self.uri}
        for r in _database.query(query2)['results']['bindings']:
            g.add((URIRef(r['s']['value']), URIRef(r['p']['value']), URIRef(self.uri)))

        return Response(
            g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(mimetype)),
            status=200,
            mimetype=mimetype
        )

    def _neighbours_html(self):
        """Returns a simple dict of Entity properties for use by a Jinja template"""
        self._make_svg_script()

        ret = {
            'uri': self.uri,
            'uri_encoded': self.uri_encoded,
            'label': self.label,
            'value': self.value,
            'script': self.script
        }

        return render_template(
            'class_entity.html',
            entity=ret
        )

    def _prov_rdf(self):
        self.g = Graph()

        # get the URIs of Named Graphs that contain references to this Entity
        q = '''
            SELECT DISTINCT ?g
            WHERE {
                GRAPH ?g {
                  {<%(uri)s> ?p ?o .}
                  UNION
                  {?s ?p2 <%(uri)s> .}
                }
            }
        ''' % {'uri': self.uri}

        # retrieve all the triple of each Named Graph containing this entity
        # add them to in-memory graph
        for row in _database.query(q)['results']['bindings']:
            q2 = '''
                CONSTRUCT {
                  ?s ?p ?o .
                }
                WHERE {
                    GRAPH <%(g)s> {
                        ?s ?p ?o .
                    }
                }
                ''' % {'g': str(row['g']['value'])}
            ng = _database.query_turtle(q2)
            self.g.parse(data=ng, format='turtle')

    def __graph_preconstruct(self):
        u = '''
            PREFIX prov: <http://www.w3.org/ns/prov#>
            DELETE {
                ?a prov:generated ?e .
            }
            INSERT {
                ?e prov:wasGeneratedBy ?a .
            }
            WHERE {
                ?a prov:generated ?e .
            }
        '''
        self.g.update(u)

    def __gen_nodes(self):
        nodes = ''

        q = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE {
                ?s a ?o .
                {?s a prov:Entity .}
                UNION
                {?s a prov:Activity .}
                UNION
                {?s a prov:Agent .}
                ?s rdfs:label ?label .
            }
            '''
        for row in self.g.query(q):
            if str(row['o']) == 'http://www.w3.org/ns/prov#Entity':
                nodes += '\t\t\t\t{id: "%(node_id)s", label: "%(label)s", shape: "ellipse", color:{background:"#FFFC87", border:"#808080"}},\n' % {
                    'node_id': row['s'],
                    'label': row['label']
                }
            elif str(row['o']) == 'http://www.w3.org/ns/prov#Activity':
                nodes += '\t\t\t\t{id: "%(node_id)s", label: "%(label)s", shape: "box", color:{background:"#9FB1FC", border:"blue"}},\n' % {
                    'node_id': row['s'],
                    'label': row['label']
                }
            elif str(row['o']) == 'http://www.w3.org/ns/prov#Agent':
                nodes += '\t\t\t\t{id: "%(node_id)s", label: "%(label)s", image: "/static/img/agent.png", shape: "image"},\n' % {
                    'node_id': row['s'],
                    'label': row['label']
                }

        return nodes

    def __gen_edges(self):
        edges = ''

        q = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE {
                ?s ?p ?o .
                ?s prov:wasAttributedTo|prov:wasGeneratedBy|prov:used|prov:wasDerivedFrom|prov:wasInformedBy ?o .
            }
            '''
        for row in self.g.query(q):
            edges += '\t\t\t\t{from: "%(from)s", to: "%(to)s", arrows:"to", font: {align: "bottom"}, color:{color:"black"}, label: "%(relationship)s"},\n' % {
                'from': row['s'],
                'to': row['o'],
                'relationship': str(row['p']).split('#')[1]
            }

        return edges

    def _make_vsjs(self):
        self.__graph_preconstruct()

        nodes = 'var nodes = new vis.DataSet([\n'
        nodes += self.__gen_nodes()
        nodes = nodes.rstrip().rstrip(',') + '\n\t\t\t]);\n'

        edges = 'var edges = new vis.DataSet([\n'
        edges += self.__gen_edges()
        edges = edges.rstrip().rstrip(',') + '\n\t\t\t]);\n'

        self.visjs = '''
            %(nodes)s

            %(edges)s

            var container = document.getElementById('network');

            var data = {
                nodes: nodes,
                edges: edges,
            };

            var options = {};
            var network = new vis.Network(container, data, options);
        ''' % {'nodes': nodes, 'edges':edges}

    def _prov_html(self):
        """Returns a simple dict of Entity properties for use by a Jinja template"""
        entity = {
            'uri': self.uri,
            'uri_encoded': self.uri_encoded,
            'label': self.label,
            'value': self.value,
        }

        self._prov_rdf()

        self._make_vsjs()

        return render_template(
            'class_entity_prov.html',
            entity=entity,
            visjs=self.visjs,
            prov_data=self.g.serialize(format='turtle')
        )

    def _get_details(self):
        """ Get the details for an Entity from an RDF triplestore"""
        # formulate the query
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
                    OPTIONAL {
                        ?wat prov:wasAttributedTo ?wat_label .
                    }
                }
            }
        ''' % {'uri': self.uri}

        # run the query
        entity_details = _database.query(query)

        # extract results into instance vars
        if entity_details and 'results' in entity_details:
            if len(entity_details['results']['bindings']) > 0:
                ret = entity_details['results']['bindings'][0]
                self.label = ret['label']['value']
                self.gat = ret['gat']['value'] if 'gat' in ret else None
                self.value = ret['v']['value'] if 'v' in ret else None
                self.wat = ret['wat']['value'] if 'wat' in ret else None
                self.wat_label = ret['wat_label']['value'] if 'wat_label' in ret else None
                self.a_u = ret['a_u']['value'] if 'a_u' in ret else None
                self.a_g = ret['a_g']['value'] if 'a_g' in ret else None

    def _make_svg_script(self):
        """ Construct the SVG code for an Entity's Neighbours view"""
        self.script = '''
                    var eLabel = "%(label)s";
                    var entity = addEntity(380, 255, eLabel, "");
            ''' % {'label': self.label if self.label is not None else 'uri'}

        self._get_value_svg()
        self._get_gat_svg()
        self._get_wat_svg()
        self._get_used_svg()
        self._get_wgb_svg()
        self._get_wdf_svg()

    def _get_value_svg(self):
        if self.value is not None:
            self.script += '''
                    var value = addValue(305, 400, "%(value)s");
                    addLink(entity, value, "prov:value", RIGHT);
                ''' % {'value': self.value}

    # TODO: implement this property of the Entity with just an additional SVG text box
    def _get_gat_svg(self):
        pass

    def _get_wat_svg(self):
        if self.wat is not None:
            uri_encoded = urllib.quote(self.wat)
            label = self.wat_label if self.wat_label is not None else 'uri'

            self.script += '''
                    var agentLabel = "%(label)s";
                    var agentUri = "%(instance_endpoint)s?_uri=%(uri_encoded)s";
                    var agent = addAgent(305, 5, agentLabel, agentUri);
                    addLink(entity, agent, "prov:wasAttributedTo", RIGHT);
                ''' % {
                    'label': label,
                    'instance_endpoint': self.endpoints['instance'],
                    'uri_encoded': uri_encoded
                }

    def _get_wgb_svg(self):
        """ Get all prov:wasGeneratedBy Activities for an Entity
        """
        script = ''
        query = '''
                PREFIX prov: <http://www.w3.org/ns/prov#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT *
                WHERE {
                    GRAPH ?g {
                        {?a prov:generated <%(uri)s> .}
                        UNION
                        {<%(uri)s> prov:wasGeneratedBy ?a.}
                        ?a rdfs:label ?label .
                    }
                }
                ''' % {'uri': self.uri}
        entity_results = _database.query(query)

        if entity_results and 'results' in entity_results:
            wgb = entity_results['results']['bindings']
            if len(wgb) == 1:
                if wgb[0].get('label'):
                    label = wgb[0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(wgb[0]['a']['value'])
                script += '''
                        var aLabel = "%(label)s";
                        var aUri = "%(instance_endpoint)s?_uri=%(uri_encoded)s";
                        var activityWGB = addActivity(5, 205, aLabel, aUri);
                        addLink(entity, activityWGB, "prov:wasGeneratedBy", TOP);
                    ''' % {
                        'label': label,
                        'instance_endpoint': self.endpoints['instance'],
                        'uri_encoded': uri_encoded
                    }
            else:
                pass

        self.script += script

    def _get_used_svg(self):
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
        entity_result = _database.query(query)

        if entity_result and 'results' in entity_result:
            used = entity_result['results']['bindings']
            if len(used) == 1:
                if used[0].get('label'):
                    label = used[0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(used[0]['a']['value'])
                script = '''
                        var aLabel = "%(label)s";
                        var aUri = "%(instance_endpoint)s?_uri=%(uri_encoded)s";
                        var activityUsed = addActivity(555, 205, aLabel, aUri);
                        addLink(activityUsed, entity, "prov:used", TOP);
                    ''' % {
                        'label': label,
                        'instance_endpoint': self.endpoints['instance'],
                        'uri_encoded': uri_encoded
                    }
            # TODO: Test, no current Entities have multiple prov:used Activities
            elif len(used) > 1:
                # TODO: Check query
                query_encoded = urllib.quote(query)
                script += '''
                        activityUsed1 = addActivity(555, 215, "", "");
                        activityUsed2 = addActivity(550, 210, "", "");
                        activityUsedN = addActivity(545, 205, "Multiple Activities, click to search", "%(sparql_endpoint)s?query=%(query_encoded)s");
                        addLink(activityUsedN, entity, "prov:used", TOP);
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
                    var activityFault = addActivity(550, 205, "There is a fault with retrieving Activities that may have used this Entity", "");
                '''

        self.script += script

    def _get_wdf_svg(self):
        """ Get the Entity/Entities this Entity prov:wasDerivedFrom"""
        script = ''
        query = '''
                PREFIX prov: <http://www.w3.org/ns/prov#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT DISTINCT ?e ?label
                WHERE {
                    GRAPH ?g {
                        <%(uri)s> prov:wasDerivedFrom ?e .
                        ?e rdfs:label ?label .
                    }
                }
                ''' % {'uri': self.uri}
        entity_results = _database.query(query)

        if entity_results and 'results' in entity_results:
            wdf = entity_results['results']['bindings']
            if len(wdf) == 1:
                if wdf[0].get('label'):
                    label = wdf[0]['label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(wdf[0]['e']['value'])
                script += '''
                        var entityWDF = addEntity(355, 440, "%(label)s", "%(instance_endpoint)s?_uri=%(uri_encoded)s");
                        drawLink(entityWDF, entity, "prov:wasDerivedFrom", TOP);
                    ''' % {
                        'label': label,
                        'instance_endpoint': self.endpoints['instance'],
                        'uri_encoded': uri_encoded
                    }
            elif len(wdf) > 1:
                query_encoded = urllib.quote(query)
                script += '''
                        var entityWDF1 = addEntity(355, 440, "", "");
                        var entityWDF2 = addEntity(350, 435, "", "");
                        var entityWDFN = addEntity(345, 430, "Multiple Entities, click here to search", "%(sparql_endpoint)s?query=%(query_encoded)s");
                        drawLink(entityWDFN, entity, "prov:wasDerivedFrom", TOP);
                    ''' % {
                        'sparql_endpoint': self.endpoints['sparql'],
                        'query_encoded': query_encoded
                    }
            else:
                # do nothing as no Entities found
                pass
        else:
            # we have a fault
            script += '''
                    var entityFaultText = addEntity(350, 440, "There is a fault with retrieving Activities that may have used this Entity", "");
                '''

        self.script += script

