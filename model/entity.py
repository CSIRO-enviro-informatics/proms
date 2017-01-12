from renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, Literal, Namespace
import urllib
import database
from modules.ldapi import LDAPI


class EntityRenderer(Renderer):
    def __init__(self, uri, endpoints):
        Renderer.__init__(self, uri, endpoints)

        self.uri_encoded = urllib.quote_plus(uri)
        self.value = None
        self.script = None

        self._get_details()

    def render(self, view, mimetype):
        if view == 'neighbours':
            # no work to be done as we have already loaded the triples
            if mimetype in LDAPI.get_rdf_mimetypes_list():
                return self._neighbours_rdf(mimetype)
            elif mimetype == 'text/html':
                return self._neighbours_html()
        if view == 'prov':
            if mimetype in LDAPI.get_rdf_mimetypes_list():
                return Response(
                    self._prov_rdf().serialize(format=LDAPI.get_rdf_parser_for_mimetype(mimetype)),
                    status=200,
                    mimetype=mimetype
                )
            elif mimetype == 'text/html':
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
        """Returns a simple dict of Entity properties for use by a Jinja template"""
        ret = {
            'uri': self.uri,
            'uri_encoded': self.uri_encoded,
            'label': self.label
        }

        if self.value is not None:
            ret['value'] = self.value

        self._make_svg_script()

        if self.script is not None:
            ret['script'] = self.script

        return render_template(
            'class_entity.html',
            entity=ret
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
            'label': self.label
        }

        if self.value is not None:
            ret['value'] = self.value

        prov_data = self._prov_rdf().serialize(format='turtle')

        return render_template(
            'class_entity_prov.html',
            entity=ret,
            prov_data=prov_data
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
        entity_details = database.query(query)

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
                    var value = addValue(305, 400, "%(value)s'");
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

