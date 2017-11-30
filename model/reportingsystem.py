from .renderer import Renderer
from flask import Response, render_template
import urllib
import _database
from modules.ldapi import LDAPI
from rdflib import Graph, URIRef, Literal, Namespace


class ReportingSystemRenderer(Renderer):
    def __init__(self, uri, endpoints):
        Renderer.__init__(self, uri, endpoints)

        self.uri_encoded = urllib.parse.quote_plus(uri)
        self.label = None
        self.aobo = None
        self.aobo_label = None
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
        """Returns a simple dict of ReportingSystem properties for use by a Jinja template"""
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
            'class_reportingsystem.html',
            reportingsystem=ret
        )

    def _prov_rdf(self):
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
            'class_reportingsystem_prov.html',
            reportingsystem=ret,
            prov_data=prov_data
        )

    def _get_details(self):
        """ Get the details for an ReportingSystem from an RDF triplestore"""
        
        query = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
            SELECT *
            WHERE {
                <%(uri)s> a proms:ReportingSystem ;
                    rdfs:label ?label .
                OPTIONAL {
                    <%(uri)s> prov:actedOnBehalfOf ?aobo .
                    ?aobo rdfs:label ?aobo_label
                }
                OPTIONAL { <%(uri)s> proms:validation ?v . }
            }
        ''' % {'uri': self.uri}
        reportingsystem = _database.query(query)

        if reportingsystem and 'results' in reportingsystem:
            if len(reportingsystem['results']['bindings']) > 0:
                ret = reportingsystem['results']['bindings'][0]
                self.label = ret['label']['value']
                if 'aobo' in ret:
                    self.aobo = ret['aobo']['value']
                    self.aobo_label = ret['aobo_label']['value']
                self.v = ret['v']['value'] if 'v' in ret else None

    def _make_svg_script(self):
        """ Construct the SVG code for a ReportingSystem's Neighbours view"""
        self.script = '''
            var rLabel = "%(label)s";
            var reportingSystem = addReportingSystem(35, 5, rLabel, "", "");
        ''' % {'label': self.label if self.label is not None else 'uri'}

        self._get_reports_svg()

    def _get_reports_svg(self):
        """ Construct SVG code for all Reports contained in a ReportingSystem"""
        query = '''
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX prov: <http://www.w3.org/ns/prov#>
                PREFIX proms: <http://promsns.org/def/proms#>
                SELECT  *
                WHERE {
                    GRAPH ?g {
                        { ?r a proms:BasicReport }
                        UNION
                        { ?r a proms:ExternalReport }
                        UNION
                        { ?r a proms:InternalReport }
                        ?r proms:wasReportedBy <%(uri)s> .
                        ?r prov:generatedAtTime ?gat .
                        ?r rdfs:label ?label .
                        ?r proms:nativeId ?nid .
                    }
                }
                ORDER BY DESC(?gat)
        ''' % {'uri': self.uri}
        reports_results = _database.query(query)

        if reports_results and 'results' in reports_results:
            reports = reports_results['results']
            if len(reports['bindings']) > 0:
                label = reports['bindings'][0]['label']['value']
                uri_encoded = urllib.quote(reports['bindings'][0]['r']['value'])
                nid = reports['bindings'][0]['nid']['value']
                y_top = 5
                x_pos = 350
                script = '''
                    var reports = [];
                    var report0 = addReport(%(x_pos)s, %(y_top)s, "%(label)s", "%(instance_endpoint)s?_uri=%(uri_encoded)s", "%(nid)s");
                    reports.push(report0);
                ''' % {
                    'x_pos': str(x_pos),
                    'y_top': str(y_top),
                    'nid': nid,
                    'label': label,
                    'instance_endpoint': self.endpoints['instance'],
                    'uri_encoded': uri_encoded,                    
                }
                if len(reports['bindings']) > 1:
                    reports = reports['bindings'][1:]
                    y_gap = 15
                    report_height = 100
                    i = 1
                    for report in reports:
                        y_offset = y_top + (i*report_height) + (i*y_gap)
                        if i == 3:
                            query_encoded = urllib.quote(query)
                            script += '''
                                var report = addReport(%(x_pos)s, %(y_offset)s, "Multiple Reports, click to search", "%(sparql_endpoint)s?query=%(query_encoded)s");
                                reports.push(report);
                            ''' % {
                                'x_pos': str(x_pos),
                                'y_offset': str(y_offset),
                                'sparql_endpoint': self.endpoints['sparql'],
                                'query_encoded': query_encoded
                            }
                            break
                        uri = report['r']['value']
                        uri_encoded = urllib.quote(uri)
                        label = report['label']['value']
                        nid = report['nid']['value']
                        script += '''
                            var report = addReport(%(x_pos)s, %(y_offset)s, "%(label)s", "%(instance_endpoint)s?_uri=%(uri_encoded)s", "%(nid)s");
                            reports.push(report);
                        ''' % {
                            'x_pos': str(x_pos),
                            'y_offset': str(y_offset),
                            'nid': nid,
                            'label': label,
                            'instance_endpoint': self.endpoints['instance'],
                            'uri_encoded': uri_encoded,
                        }
                        i += 1
                script += '''
                    addConnectedLinks(reportingSystem, reports, "proms:reportingSystem");
                '''
            else:
                # no reports
                script = ''
        else:
            # we have a fault
            script = '''
                //var reportUsedFaultText = addReport(550, 200, "There is a fault with retrieving Reports that may have used this ReportingSystem", "");
                var reportUsedFaultText = addReport(550, 0, "No Reports for this RS", "");
            '''

        self.script += script
