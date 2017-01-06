from renderer import Renderer
from flask import Response, render_template
import urllib
import database
from modules.ldapi import LDAPI


class ReportingSystemRenderer(Renderer):
    def __init__(self, uri, endpoints):
        Renderer.__init__(self, uri, endpoints)

        self.uri_encoded = urllib.quote_plus(uri)
        self.label = None
        self.script = None

    def render(self, view, mimetype):
        if view == 'neighbours':
            # no work to be done as we have already loaded the triples
            if mimetype in LDAPI.get_rdf_mimetypes_list():
                return self._neighbours_rdf(mimetype)
            elif mimetype == 'text/html':
                return self._neighbours_html()
        # elif model == 'prov':
        #     # remove all the non-PROV-O (and RDF) triples
        #     self.g.update(
        #         '''
        #         DELETE { ?s ?p ?o }
        #         WHERE {
        #             ?s ?p ?o .
        #             FILTER (!REGEX(STR(?p), "http://www.w3.org/ns/prov#") &&
        #                 !(STR(?p) = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"))
        #         }
        #         '''
        #     )
        #     if format in LDAPI.MIMETYPES_PARSERS.iterkeys():
        #         return Response(
        #             self.g.serialize(format=LDAPI.MIMETYPES_PARSERS.get(format)),
        #             status=200,
        #             mimetype=format
        #         )
        #     else:  # HTML
        #         return render_template('class_reportingrystem_prov.html')

    def _neighbours_rdf(self, mimetype):
        return Response(
            self.g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(mimetype)),
            status=200,
            mimetype=mimetype
        )

    def _neighbours_html(self):
        """Returns a simple dict of ReportingSystem properties for use by a Jinja template"""
        ret = {
            'uri': self.uri,
            'uri_encoded': self.uri_encoded,
            'label': self.label
        }

        if self.script is not None:
            ret['script'] = self.script

        return render_template(
            'class_reportingsystem.html',
            entity=ret
        )

    def _get_details(self):
        """ Get the details for an ReportingSystem from an RDF triplestore"""
        
        query = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
            SELECT *
            WHERE {
              <%(uri)s> a proms:ReportingSystem .
              <%(uri)s> rdfs:label ?label .
              OPTIONAL { <%(uri)s> proms:validation ?v . }
            }
        ''' % {'uri': self.uri}
        reportingsystem = sparqlqueries.query(query)

        if reportingsystem and 'results' in reportingsystem:
            if len(reportingsystem['results']['bindings']) > 0:
                ret = reportingsystem['results']['bindings'][0]
                self.label = reportingsystem['label']['value']
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
        script = ''
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
        reports_results = database.query(query)

        if reports_results and 'results' in reports_results:
            reports = reports_results['results']
            if len(reports['bindings']) > 0:
                label = reports['bindings'][0]['label']['value']
                uri_encoded = urllib.quote(reports['bindings'][0]['r']['value'])
                nid = reports['bindings'][0]['nid']['value']
                y_top = 5
                x_pos = 350
                reports_script = '''
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
                            reports_script += '''
                                var report = addReport(%(x_pos)s, %(y_offset)s', "Multiple Reports, click to search", "%(sparql_endpoint)s?query=%(query_encoded)s");
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
                        reports_script += '''
                            var report = addReport(%(x_pos)s, %(y_offset)s, "%(label)s'", "%(instance_endpoint)s?_uri=%(uri_encoded)s", "%(nid)s");
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
                reports_script += '''
                    addConnectedLinks(reportingSystem, reports, "proms:reportingSystem");
                '''
            else:
                # no reports
                reports_script = ''
        else:
            # we have a fault
            reports_script = '''
                //var reportUsedFaultText = addReport(550, 200, "There is a fault with retrieving Reports that may have used this ReportingSystem", "");
                var reportUsedFaultText = addReport(550, 0, "No Reports for this RS", "");
            '''
        return reports_script
