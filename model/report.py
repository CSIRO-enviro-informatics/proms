from .renderer import Renderer
from flask import Response, render_template
import urllib
import database
from modules.ldapi import LDAPI
from rdflib import Graph, URIRef, Literal, Namespace


class ReportRenderer(Renderer):
    def __init__(self, uri, endpoints):
        Renderer.__init__(self, uri, endpoints)

        self.uri_encoded = urllib.quote_plus(uri)
        self.label = None
        self.rt = None
        self.rt_label = None
        self.nid = None
        self.gat = None
        self.rs = None
        self.rs_encoded = None
        self.rs_label = None        
        self.sa = None
        self.sa_label = None
        self.ea = None
        self.ea_label = None
        self.script = None

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
            'rt_label': self.rt_label,
            'uri': self.uri,
            'uri_encoded': self.uri_encoded,
            'label': self.label,
            'nid': self.nid,
            'gat': self.gat,
            'rs_encoded': self.rs_encoded,
            'rs_label': self.rs_label,
            'sa': self.sa,
            'ea': self.ea,
            'script': self.script
        }

        return render_template(
            'class_report.html',
            report=ret
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
            'rt_label': self.rt_label,
            'uri': self.uri,
            'uri_encoded': self.uri_encoded,
            'label': self.label,
            'nid': self.nid,
            'gat': self.gat,
            'rs_encoded': self.rs_encoded,
            'rs_label': self.rs_label,
            'sa': self.sa,
            'ea': self.ea
        }

        prov_data = self._prov_rdf().serialize(format='turtle')

        return render_template(
            'class_report_prov.html',
            report=ret,
            prov_data=prov_data
        )

    def _get_details(self):
        """ Get the details for a Report from an RDF triplestore"""
        # formulate the query
        query = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE {
                GRAPH ?g {
                    <%(uri)s>
                        a ?rt ;
                        rdfs:label ?label ;
                        proms:nativeId ?nid ;
                        prov:generatedAtTime ?gat ;
                        proms:wasReportedBy ?rs .
                    OPTIONAL {
                       ?rs rdfs:label ?rs_label .
                    }
                    OPTIONAL {
                        <%(uri)s>
                            proms:startingActivity ?sa .
                            ?sa rdfs:label ?sa_label .
                    }
                    OPTIONAL {
                        <%(uri)s>
                            proms:endingActivity ?ea .
                            ?ea rdfs:label ?ea_label .
                    } .
                }
            }
        ''' % {'uri': self.uri}

        # run the query
        report_details = database.query(query)

        # extract results into instance vars
        if report_details and 'results' in report_details:
            if len(report_details['results']['bindings']) > 0:
                ret = report_details['results']['bindings'][0]
                self.rt = ret['rt']['value']
                if 'Basic' in self.rt:
                    self.rt_label = 'Basic'
                elif 'Internal' in self.rt:
                    self.rt_label = 'Internal'
                elif 'External' in self.rt:
                    self.rt_label = 'External'
                self.label = ret['label']['value']
                self.nid = ret['nid']['value']
                self.gat = ret['gat']['value']
                self.rs = ret['rs']['value']
                self.rs_encoded = urllib.quote_plus(self.rs)
                self.rs_label = ret['rs_label']['value'] if 'rs_label' in ret else self.rs
                if 'sa' in ret:
                    self.sa = ret['sa']['value']
                    self.sa_label = ret['sa_label']['value']
                if 'ea' in ret:
                    self.ea = ret['ea']['value']
                    self.ea_label = ret['ea_label']['value']

    def _make_svg_script(self):
        """ Construct the SVG code for a Report's Neighbours view"""
        self.script = '''
            var rLabel = "%(label)s";
            var report = addReport(350, 200, rLabel, "");
        ''' % {'label': self.label}

        self.script += '''
            var rsUri = "%(instance_endpoint)s?_uri=%(uri_encoded)s";
            var rsLabel = "%(label)s";
            var repSystem = addReportingSystem(350, 20, rsLabel, rsUri);
            addLink(report, repSystem, "proms:reportingSystem", RIGHT);
        ''' % {
            'instance_endpoint': self.endpoints['instance'],
            'uri_encoded': self.rs_encoded,
            'label': self.rs_label
        }

        if self.sa is not None and self.ea is not None:
            if self.sa == self.ea:
                # External Report -- single Activity
                self.script += '''
                    var uri = "%(instance_endpoint)s?_uri=%(uri_encoded)s";
                    var label = "%(label)s";
                    var activity = addActivity(50, 200, label, uri);
                    addLink(report, activity, "proms:startingActivity", TOP);
                    addLink(report, activity, "proms:endingActivity", BOTTOM);
                ''' % {
                    'instance_endpoint': self.endpoints['instance'],
                    'uri_encoded': urllib.quote(self.sa),
                    'label': self.sa_label
                }
            else:
                # Internal Report -- 2 Activities
                self.script += '''
                    var saUri = "%(instance_endpoint)s?_uri=%(uri_encoded)s";
                    var saLabel = "%(label)s";
                    var sacActivity = addActivity(50, 120, sacLabel, sacUri);
                    addLink(report, sacActivity, "proms:startingActivity", TOP);
                ''' % {
                    'instance_endpoint': self.endpoints['instance'],
                    'uri_encoded': urllib.quote(self.sa),
                    'label': self.sa_label
                }

                self.script += '''
                    var eacUri = "%(instance_endpoint)s?_uri=%(uri_encoded)s";
                    var eacLabel = "%(label)s";
                    var eacActivity = addActivity(50, 280, eacLabel, eacUri);
                    addLink(report, eacActivity, "proms:endingActivity", BOTTOM);
                ''' % {
                    'instance_endpoint': self.endpoints['instance'],
                    'uri_encoded': urllib.quote(self.ea),
                    'label': self.ea_label
                }
        else:
            # Basic Report -- no Activities
            pass
