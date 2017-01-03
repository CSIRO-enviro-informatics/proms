from flask import Response, render_template
import urllib
import database.get_things
import settings
from modules.ldapi import LDAPI


class ReportRenderer:
    def __init__(self, g, uri):
        # load Entity data from given graph
        self.g = g
        self.uri = uri

    def render_view_format(self, view, mimetype):
        """
        Renders a model and format of an Report

        No validation is needed as the model and format for an Report are pre-validated before this class is
        instantiated
        :param view: An allowed model model of an Report
        :param mimetype: An allowed format of an Report
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
                    'class_report.html',
                    uri=self.uri,
                    report=self.get_report(),
                    web_subfolder=settings.WEB_SUBFOLDER
                )

    def _get_details_query(self):
        """ Get details for a a Report (JSON)
        """
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
                        proms:wasReportedBy ?rs .
                    OPTIONAL {
                        <%(uri)s>
                            proms:startingActivity ?sac .
                            ?sac prov:startedAtTime ?sat .
                            ?sac rdfs:label ?sac_t
                    } .
                    OPTIONAL {
                        <%(uri)s>
                            proms:endingActivity ?eac .
                            ?eac prov:endedAtTime ?eat .
                            ?eac rdfs:label ?eac_t .
                    } .
                }
            }
        ''' % {'uri': self.uri}
        res = database.query(query)
        return res
    
    def get_report(self):
        """ Get details for a Report (dict)
        """
        report_details = self._get_details_query()
        ret = {}
        # Check this
        if report_details and 'results' in report_details:
            if len(report_details['results']['bindings']) > 0:
                index = 0
                if len(report_details['results']['bindings']) > 1:
                    index = 1
                ret = report_details['results']['bindings'][index]

                # label
                ret['label'] = ret['label']['value']

                # Report type
                ret['rt'] = ret['rt']['value']
                if 'Basic' in ret['rt']:
                    ret['rt_str'] = 'Basic'
                elif 'Internal' in ret['rt']:
                    ret['rt_str'] = 'Internal'
                elif 'External' in ret['rt']:
                    ret['rt_str'] = 'External'

                # nativeId
                ret['nid'] = ret['nid']['value']

                # ReportingSystem
                ret['rs'] = urllib.quote(ret['rs']['value'])

                if 'rs_t' in report_details['results']['bindings'][0]:
                    ret['rs_t'] = ret['rs_t']['value']
                if 'sac' in report_details['results']['bindings'][0]:
                    ret['sac'] = ret['sac']['value']
                    if 'sat' in report_details['results']['bindings'][0]:
                        ret['sat'] = ret['sat']['value']
                    if 'sac_t' in report_details['results']['bindings'][0]:
                        ret['sac_t'] = ret['sac_t']['value']
                if 'eac' in report_details['results']['bindings'][0]:
                    ret['eac'] = ret['eac']['value']
                    if 'eat' in report_details['results']['bindings'][0]:
                        ret['eat'] = ret['eat']['value']
                    if 'eac_t' in report_details['results']['bindings'][0]:
                        ret['eac_t'] = ret['eac_t']['value']
                ret['uri'] = self.uri
                ret['uri_html'] = urllib.quote(self.uri)
                svg_script = self._get_svg(ret)
                if svg_script[0]:
                    ret['r_script'] = svg_script[1]
        return ret

    def _get_svg(self, report_dict):
        """ Construct the SVG code for a Report
        """
        rLabel = report_dict.get('label', 'uri')
        script = '''
            var rLabel = "''' + rLabel + '''";
            var report = addReport(350, 200, rLabel, "");
        '''
        if report_dict.get('rs'):
            rsLabel = report_dict.get('rs_t', 'uri')
            rsUri = report_dict.get('rs', '')
            if rsUri != '':
                rsUri = settings.WEB_SUBFOLDER + "/instance?_uri=" + rsUri
            script += '''
                var rsLabel = "''' + rsLabel + '''";
                var rsUri = "''' + rsUri + '''";
                var repSystem = addReportingSystem(350, 20, rsLabel, rsUri);
                addLink(report, repSystem, "proms:reportingSystem", RIGHT);
            '''
        if report_dict.get('sac'):
            sac_uri = report_dict.get('sac')
            sac_uri_encoded = urllib.quote(sac_uri)
            sac_label = report_dict.get('sac_t', 'uri')
            script += '''
                var sacUri = "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + sac_uri_encoded + '''";
                var sacLabel = "''' + sac_label + '''";
            '''
            eac_uri = ''
            if report_dict.get('eac'):
                eac_uri = report_dict.get('eac')
                eac_uri_encoded = urllib.quote(eac_uri)
                eac_label = report_dict.get('eac_t', 'uri')
            if sac_uri == eac_uri or eac_uri=='':
                script += '''
                    var activity = addActivity(50, 200, sacLabel, sacUri);
                    addLink(report, activity, "proms:startingActivity", TOP);
                '''
            elif eac_uri != '':
                script += '''
                    var eacUri = "''' + settings.WEB_SUBFOLDER + "/instance?_uri=" + eac_uri_encoded + '''";
                    var eacLabel = "''' + eac_label + '''";
                    var sacActivity = addActivity(50, 120, sacLabel, sacUri);
                    addLink(report, sacActivity, "proms:startingActivity", TOP);
                    var eacActivity = addActivity(50, 280, eacLabel, eacUri);
                    addLink(report, eacActivity, "proms:endingActivity", BOTTOM);
                '''
        return [True, script]
