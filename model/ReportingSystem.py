from flask import Response, render_template
import urllib
import settings
from database import sparqlqueries
from modules.ldapi import LDAPI


class ReportingSystemRenderer:
    def __init__(self, g, uri):
        # load Entity data from given graph
        self.g = g
        self.uri = uri

    def render_view_format(self, view, mimetype):
        """
        Renders a model and format of an ReportingSystem

        No validation is needed as the model and format for an ReportingSystem are pre-validated before this class is
        instantiated
        :param view: An allowed model model of an ReportingSystem
        :param format: An allowed format of an ReportingSystem
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
                    'class_reportingsystem.html',
                    reportingsystem=self.get_details()
                )
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

    def get_details(self):
        """ Get details for a ReportingSystem
        """
        query = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX proms: <http://promsns.org/def/proms#>
            PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
            SELECT ?title ?fn ?o ?em ?ph ?add ?v
            WHERE {
              <%(uri)s> a proms:ReportingSystem .
              <%(uri)s> rdfs:label ?title .
              OPTIONAL { <%(uri)s> proms:validation ?v . }
            }
        ''' % {'uri': self.uri}
        reportingsystem_detail = sparqlqueries.query(query)
        ret = {}
        if reportingsystem_detail and 'results' in reportingsystem_detail:
            if len(reportingsystem_detail['results']['bindings']) > 0:
                ret['title'] = reportingsystem_detail['results']['bindings'][0]['title']['value']
                if 'v' in reportingsystem_detail['results']['bindings'][0]:
                    ret['v'] = reportingsystem_detail['results']['bindings'][0]['v']['value']
                ret['uri'] = self.uri

                svg_script = self.get_svg(ret)
                if svg_script[0]:
                    rs_script = svg_script[1]
                    rs_script += self._get_reports_svg()
                    ret['rs_script'] = rs_script
        return ret

    def get_svg(self, reportingsystem_dict):
        """ Construct the SVG code for the ReportingSystem
        """
        rLabel = reportingsystem_dict.get('title', 'Untitled')
        script = '''
            var rLabel = "''' + rLabel + '''";
            var reportingSystem = addReportingSystem(35, 5, rLabel, "", "");
        '''
        return [True, script]

    def _get_reports_svg(self):
        """ Construct SVG code for all Reports contained in a ReportingSystem
        """
        reports = self._get_reports()
        if reports and reports['results']['bindings']:
            if len(reports['results']['bindings']) > 0:
                r1uri_encoded = urllib.quote(reports['results']['bindings'][0]['r']['value'])
                r1title = reports['results']['bindings'][0]['title']['value']
                r1jobId = reports['results']['bindings'][0]['nid']['value']
                y_top = 5
                x_pos = 350
                reports_script = '''
                    var reports = [];
                    var report0 = addReport(''' + str(x_pos) + ''', ''' + str(y_top) + ''', "''' + r1title + \
                                 '''", "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + r1uri_encoded + \
                                 '''", "''' + r1jobId + '''");
                    reports.push(report0);
                '''
                if len(reports['results']['bindings']) > 1:
                    reports = reports['results']['bindings'][1:]
                    y_gap = 15
                    report_height = 100
                    i = 1
                    for report in reports:
                        y_offset = y_top + (i*report_height) + (i*y_gap)
                        if i == 3:
                            query = self._get_reports_query()
                            query_encoded = urllib.quote(query)
                            reports_script += '''
                                var report = addReport(''' + str(x_pos) + ''', ''' + str(y_offset) + \
                                              ''', "Multiple Reports, click to search", "''' + \
                                              settings.WEB_SUBFOLDER + "/function/sparql?query=" + \
                                              query_encoded + '''");
                                reports.push(report);
                            '''
                            break
                        uri = report['r']['value']
                        uri_encoded = urllib.quote(uri)
                        title = report['title']['value']
                        jobId = report['nid']['value']
                        reports_script += '''
                            var report = addReport(''' + str(x_pos) + ''', ''' + str(y_offset) + ''', "''' + \
                                          title + '''", "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + \
                                          uri_encoded + '''", "''' + jobId + '''");
                            reports.push(report);
                        '''
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

    def _get_reports_query(self):
        return '''
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
                        ?r rdfs:label ?title .
                        ?r proms:nativeId ?nid .
                    }
                }
                ORDER BY DESC(?gat)
        ''' % {'uri': self.uri}

    def _get_reports(self):
        """ Get all Reports for a ReportingSystem
        """
        q = self._get_reports_query()
        res = sparqlqueries.query(q)
        return res
