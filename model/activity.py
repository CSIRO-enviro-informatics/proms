from .renderer import Renderer
from flask import Response, render_template
import urllib
import database
from modules.ldapi import LDAPI
from rdflib import Graph, URIRef, Literal, Namespace


class ActivityRenderer(Renderer):
    def __init__(self, uri, endpoints):
        Renderer.__init__(self, uri, endpoints)

        self.uri_encoded = urllib.quote_plus(uri)
        self.label = None
        self.sat = None
        self.eat = None
        self.waw = None
        self.waw_encoded = None
        self.waw_label = None
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
            'sat': self.sat,
            'eat': self.eat,
            'waw_encoded': self.waw_encoded,
            'waw_label': self.waw_label,
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
            'sat': self.sat,
            'eat': self.eat,
            'waw_encoded': self.waw_encoded,
            'waw_label': self.waw_label
        }

        prov_data = self._prov_rdf().serialize(format='turtle')

        return render_template(
            'class_activity_prov.html',
            activity=ret,
            prov_data=prov_data
        )

    def _get_details(self):
        """ Get the details of an Activity from an RDF triplestore"""
        # formulate the query
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
                        ?waw a prov:Agent .
                        ?waw rdfs:label ?waw_label .
                    }
                }
            }
        ''' % {'uri': self.uri}

        # run the query
        activity_details = database.query(query)

        # extract results into instance vars
        if activity_details and 'results' in activity_details:
            if len(activity_details['results']['bindings']) > 0:
                ret = activity_details['results']['bindings'][0]
                self.label = ret['label']['value']
                self.sat = ret['sat']['value'] if 'sat' in ret else None
                self.eat = ret['eat']['value'] if 'eat' in ret else None
                if 'waw' in ret:
                    self.waw = ret['waw']['value']
                    self.waw_encoded = urllib.quote_plus(self.waw)
                    self.waw_label = ret['waw_label']['value']

    def _make_svg_script(self):
        """ Construct the SVG code for an Activity's Neighbours view"""
        self.script = '''
                var aLabel = "%(label)s";
                var activity = addActivity(275, 200, aLabel, "");
        ''' % {'label': self.label if self.label is not None else 'uri'}

        self._get_waw_svg()
        self._get_used_svg()
        self._get_generated_svg()
        self._get_wif_svg()

    def _get_waw_svg(self):
        if self.waw is not None:
            uri_encoded = urllib.quote(self.waw)
            label = self.waw_label if self.waw_label is not None else 'uri'

            self.script += '''
                var agentName = "%(label)s";
                var agentUri = "%(instance_endpoint)s?_uri=%(uri_encoded)s";
                var agent = addAgent(275, 5, agentName, agentUri);
                addLink(activity, agent, "prov:wasAssociatedWith", RIGHT);
            ''' % {
                'label': label,
                'instance_endpoint': self.endpoints['instance'],
                'uri_encoded': uri_encoded
            }

    def _get_used_svg(self):
        """ Construct the SVG code for the prov:used Entities of an Activity"""
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
                    var entityUsed1 = addEntity(105, 250, "%(label)s", "%(instance_endpoint)s?_uri=%(uri_encoded)s");
                    addLink(activity, entityUsed1, "prov:used", TOP);
                ''' % {
                    'label': label,
                    'instance_endpoint': self.endpoints['instance'],
                    'uri_encoded': uri_encoded
                }
                if len(used['bindings']) > 1:
                    if used['bindings'][1].get('u_label'):
                        u_label = used['bindings'][1]['u_label']['value']
                    else:
                        u_label = 'uri'
                    uri_encoded = urllib.quote(used['bindings'][1]['u']['value'])

                    script += '''
                        var entityUsed2 = addEntity(105, 100, "%(u_label)s", "%(inst_end)s?_uri=%(uri_encoded)s");
                        addLink(activity, entityUsed2, "prov:used", TOP);
                    ''' % {
                        'u_label': u_label,
                        'inst_end': self.endpoints['instance'],
                        'uri_encoded': uri_encoded
                    }
                    if len(used['bindings']) == 3:
                        if used['bindings'][2].get('u_label'):
                            u_label = used['bindings'][2]['u_label']['value']
                        else:
                            u_label = 'uri'
                        uri_encoded = urllib.quote(used['bindings'][2]['u']['value'])

                        script += '''
                            var entityUsed3 = addEntity(105, 400, "%(u_label)s", "%(inst_end)s?_uri=%(uri_encoded)s");
                            addLink(activity, entityUsed3, "prov:used", RIGHT);
                        ''' % {
                            'u_label': u_label,
                            'inst_end': self.endpoints['instance'],
                            'uri_encoded': uri_encoded
                        }
                    elif len(used['bindings']) > 3:
                        query_encoded = urllib.quote(query)
                        script = ''  # reset script
                        script += '''
                            var entityUsed1 = addEntity(105, 260, "", "");
                            var entityUsed2 = addEntity(100, 255, "", "");
                            var entityUsedN = addEntity(95, 250, "Multiple Entities, click to search", ''' \
                            '''"%(sparql_endpoint)s?query=%(query_encoded)s");
                            addLink(activity, entityUsedN, "prov:used", TOP);
                        ''' % {
                            'sparql_endpoint': self.endpoints['sparql'],
                            'query_encoded': query_encoded
                        }
            else:
                # do nothing as no Agents found
                pass
        else:
            # we have a fault
            script += 'var entityUsedFaultText = addEntity(1, 200, ' \
                      '"There is a fault with retrieving Entities that may have been used by this Activity", "");'

        self.script += script

    def _get_generated_svg(self):
        """ Construct the SVG code for the prov:generated Entities of an Activity"""
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
                        OPTIONAL {?u rdfs:label ?wgb_label .}
                    }
                }
                ''' % {'uri': self.uri}

        activity_results = database.query(query)
        if activity_results and 'results' in activity_results:
            gen = activity_results['results']
            if len(gen['bindings']) > 0:
                if gen['bindings'][0].get('wgb_label'):
                    wgb_label = gen['bindings'][0]['wgb_label']['value']
                else:
                    wgb_label = 'uri'
                uri_encoded = urllib.quote(gen['bindings'][0]['u']['value'])
                script += '''
                    var entityGen1 = addEntity(605, 250, "%(wgb_label)s", "%(instance_endpoint)s?_uri=%(uri_encoded)s");
                    addLink(activity, entityGen1, "prov:generated", TOP);
                ''' % {
                    'wgb_label': wgb_label,
                    'instance_endpoint': self.endpoints['instance'],
                    'uri_encoded': uri_encoded
                }
                if len(gen['bindings']) > 1:
                    if gen['bindings'][1].get('wgb_label'):
                        wgb_label = gen['bindings'][1]['wgb_label']['value']
                    else:
                        wgb_label = 'uri'
                    uri_encoded = urllib.quote(gen['bindings'][1]['u']['value'])

                    script += '''
                        var entityGen2 = addEntity(605, 100, "%(wgb_label)s", "%(inst_endpoint)s?_uri=%(uri_encoded)s");
                        addLink(activity, entityGen2, "prov:generated", TOP);
                    ''' % {
                        'wgb_label': wgb_label,
                        'inst_endpoint': self.endpoints['instance'],
                        'uri_encoded': uri_encoded
                    }
                    if len(gen['bindings']) == 3:
                        if gen['bindings'][2].get('wgb_label'):
                            wgb_label = gen['bindings'][2]['wgb_label']['value']
                        else:
                            wgb_label = 'uri'
                        uri_encoded = urllib.quote(gen['bindings'][2]['u']['value'])

                        script += '''
                            var entityGen3 = addEntity(605, 400, "%(wgb_label)s", "%(inst_end)s?_uri=%(uri_encoded)s");
                            addLink(activity, entityGen3, "prov:generated", TOP);
                        ''' % {
                            'wgb_label': wgb_label,
                            'inst_end': self.endpoints['instance'],
                            'uri_encoded': uri_encoded
                        }
                    elif len(gen['bindings']) > 3:
                        # TODO: Check query
                        query_encoded = urllib.quote(query)
                        script = ''  # reset script
                        script += '''
                            var entityGen1 = addEntity(615, 260, "", "");
                            var entityGen2 = addEntity(610, 255, "", "");
                            var entityGenN = addEntity(605, 250, "Multiple Entities, click here to search", ''' \
                            '''%(sparql_endpoint)s?query=%(query_encoded)s");
                            addLink(activity, entityGenN, "prov:generated", TOP);
                        ''' % {'sparql_endpoint': self.endpoints['sparql'], 'query_encoded': query_encoded}
            else:
                # zero
                pass
        else:
            # we have a fault
            script += '''
                var entityGenFaultText = addEntity(349, 200, '''\
                '''"There is a fault with retrieving Entities that may have been used by this Activity", "");
            '''

        self.script += script

    def _get_wif_svg(self):
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
                        OPTIONAL { ?wif rdfs:label ?wif_label . }
                    }
                }
                ''' % {'uri': self.uri}
        activity_results = database.query(query)

        if activity_results and 'results' in activity_results:
            wif = activity_results['results']
            if len(wif['bindings']) == 1:
                if wif['bindings'][0].get('wif_label'):
                    label = wif['bindings'][0]['wif_label']['value']
                else:
                    label = 'uri'
                uri_encoded = urllib.quote(wif['bindings'][0]['wif']['value'])
                script += '''
                    var activityWIB = addActivity(275, 399, "%(label)s", "%(instance_endpoint)s?_uri=%(uri_encoded)s");
                    addLink(activity, activityWIB, "prov:wasInformedBy", RIGHT);
                ''' % {
                    'label': label,
                    'instance_endpoint': self.endpoints['instance'],
                    'uri_encoded': uri_encoded
                }
            # TODO: Check query
            elif len(wif['bindings']) > 1:
                query_encoded = urllib.quote(query)
                script += '''
                    var activityWIB1 = addActivity(275, 399, "", "");
                    var activityWIB2 = addActivity(270, 394, "", "")
                    var activityWIBN = addActivity(2650, 389, "Multiple Activities, click here to search", "%(sparql_endpoint)s?query=%(query_encoded)s");
                    addLink(activity, activityWIBN, "prov:wasInformedBy", RIGHT);
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
                var activityUsedFaultText = addActivity(550, 200, "There is a fault with retrieving Activities that may have used this Entity", "");
            '''

        self.script += script
