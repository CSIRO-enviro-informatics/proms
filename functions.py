import functions_db
import functions_db
import settings
import json
import cStringIO
from rdflib import Graph
import requests
#import rules_proms
from rulesets import proms
from rulesets import reportingsystems
#from rulesets import proms_report
#from rulesets.rules_proms import proms_report
import urllib
import re
import uuid


#
#   ReportingSystems
#
def get_reportingsystems_dict():
    query = '''
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?rs ?t
        WHERE {
          ?rs a proms:ReportingSystem .
          ?rs rdf:label ?t .
        }
    '''
    reportingsystems = functions_db.db_query_secure(query)
    reportingsystem_items = []
    # Check if nothing is returned
    if reportingsystems and 'results' in reportingsystems:
        for reportingsystem in reportingsystems['results']['bindings']:
            ret = {}
            ret['rs'] = urllib.quote(str(reportingsystem['rs']['value']))
            ret['rs_u'] = str(reportingsystem['rs']['value'])
            if reportingsystem.get('t'):
                ret['t'] = str(reportingsystem['t']['value'])
            reportingsystem_items.append(ret)
    return reportingsystem_items


def get_reportingsystem_dict(reportingsystem_uri):
    query = '''
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        SELECT ?t ?fn ?o ?em ?ph ?add
        WHERE {
          <''' + reportingsystem_uri + '''> a proms:ReportingSystem .
          <''' + reportingsystem_uri + '''> rdf:label ?t .
          OPTIONAL { <''' + reportingsystem_uri + '''> proms:owner ?o . }
          OPTIONAL { ?o vcard:fn ?fn . }
          OPTIONAL { ?o vcard:hasEmail ?em . }
          OPTIONAL { ?o vcard:hasTelephone ?ph_1 . }
          OPTIONAL { ?ph_1 vcard:hasValue ?ph . }
          OPTIONAL { ?o vcard:hasAddress ?add_1 . }
          OPTIONAL { ?add_1 vcard:locality ?add }
        }
    '''
    reportingsystem_detail = functions_db.db_query_secure(query)
    ret = {}
    if reportingsystem_detail and 'results' in reportingsystem_detail:
        if len(reportingsystem_detail['results']['bindings']) > 0:
            ret['t'] = reportingsystem_detail['results']['bindings'][0]['t']['value']
            if 'fn' in reportingsystem_detail['results']['bindings'][0]:
                ret['fn'] = reportingsystem_detail['results']['bindings'][0]['fn']['value']
            if 'o' in reportingsystem_detail['results']['bindings'][0]:
                ret['o'] = reportingsystem_detail['results']['bindings'][0]['o']['value']
            if 'em' in reportingsystem_detail['results']['bindings'][0]:
                ret['em'] = reportingsystem_detail['results']['bindings'][0]['em']['value']
            if 'ph' in reportingsystem_detail['results']['bindings'][0]:
                ret['ph'] = reportingsystem_detail['results']['bindings'][0]['ph']['value']
            if 'add' in reportingsystem_detail['results']['bindings'][0]:
                ret['add'] = reportingsystem_detail['results']['bindings'][0]['add']['value']
            ret['uri'] = reportingsystem_uri
            ret['rs_script'] = get_reportingsystem_reports_svg(reportingsystem_uri)
    return ret


def draw_report(n, uri, title, nativeId, drawArrow):
    y_offset = n * 130
    y1 = y_offset + 16
    y2 = y_offset + 16
    y3 = y_offset + 97
    y4 = y_offset + 117
    y5 = y_offset + 117
    y_label = y_offset + 40

    svg = '''
        //Report
        var report1 = svgContainer.append("polygon")
                                .attr("stroke", "grey")
                                .attr("stroke-width", "1")
                                .attr("fill", "MediumVioletRed")
                                .attr("points", "250,''' + str(y1) + ''' 390,''' + str(y2) + ''' 390,''' + str(y3) + ''' 370,''' + str(y4) + ''' 250,''' + str(y5) + '''");

        //Report class name
        var reportName = svgContainer.append("text")
                                .attr("x", 320)
                                .attr("y", ''' + str(y_label) + ''')
                                .text("Report")
                                .style("font-family", "Verdana")
                                .style("fill", "white")
                                .style("text-anchor", "middle");
    '''

    if uri:
        uri_encoded = urllib.quote(uri)
        svg += '''
            //Report N title
            var entityTitle = svgContainer.append('foreignObject')
                                    .attr('x', 250)
                                    .attr('y', ''' + str(y_offset + 47) + ''')
                                    .attr('width', 138)
                                    .attr('height', 95)
                                    .append("xhtml:body")
                                    .html('<div style="width:138px; color:white; font-size:smaller; background-color:MediumVioletRed;"><a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/report/?uri=''' + uri_encoded + '''">''' + title + '''</a><br />nativeId: ''' + nativeId + '''</div>')
            '''
    else:
        svg += '''
            //Report N title
            var reportTitle = svgContainer.append("text")
                                            .attr("x", 320)
                                            .attr("y", 200)
                                            .text("''' + title + '''")
                                            .style("font-family", "Verdana")
                                            .style("font-size", "12px")
                                            .style("text-anchor", "middle");
        '''

    if drawArrow:
        ya1 = y_offset + 49
        ya2 = y_offset + 49
        ya3 = y_offset + 44
        ya4 = y_offset + 50
        ya5 = y_offset + 57
        ya6 = y_offset + 51
        ya7 = y_offset + 51
        svg += '''
            //Report N arrow
            var reportNArrow = svgContainer.append("polygon")
                                    .style("stroke-width", "1")
                                    .attr("points", "250,''' + str(ya1) + ''' 192,''' + str(ya1) + ''' 192,''' + str(ya1-130) + ''' 190,''' + str(ya1-130) + ''' 190,''' + str(ya6) + ''' 250,''' + str(ya6) + ''' ");
        '''
    return svg


def get_reportingsystem_reports_svg(reportingsystem_uri):
    #add in all the Reports for this ReportingSystem
    query = '''
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT  *
        WHERE { GRAPH ?g {
          {?r a proms:Report}
          UNION
          {?r a proms:BasicReport}
          UNION
          {?r a proms:ExternalReport}
          UNION
          {?r a proms:InternalReport}
          ?r proms:reportingSystem <''' + reportingsystem_uri + '''> .
          ?r rdf:label ?t .
          ?r proms:nativeId ?job .
          ?r proms:endingActivity ?sat .
          ?sat prov:endedAtTime ?eat .
        } }
        ORDER BY DESC(?eat)
    '''
    reports = functions_db.db_query_secure(query)
    if reports and reports['results']['bindings']:
        if len(reports['results']['bindings']) > 0:
            r1uri_encoded = urllib.quote(reports['results']['bindings'][0]['r']['value'])
            r1title = reports['results']['bindings'][0]['t']['value']
            r1jobId = reports['results']['bindings'][0]['job']['value']
            reports_script = '''
            //Report
            var report1 = svgContainer.append("polygon")
                                    .attr("stroke", "grey")
                                    .attr("stroke-width", "1")
                                    .attr("fill", "MediumVioletRed")
                                    .attr("points", "250,16 390,16 390,97 370,117 250,117");

            //Report class name
            var reportName = svgContainer.append("text")
                                    .attr("x", 320)
                                    .attr("y", 40)
                                    .text("Report")
                                    .style("font-family", "Verdana")
                                    .style("fill", "white")
                                    .style("text-anchor", "middle");

            //Report 1 title
            var entityTitle = svgContainer.append('foreignObject')
                                    .attr('x', 250)
                                    .attr('y', 47)
                                    .attr('width', 138)
                                    .attr('height', 95)
                                    .append("xhtml:body")
                                    .html('<div style="width:138px; color:white; font-size:smaller; background-color:MediumVioletRed;"><a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/report/?uri=''' + r1uri_encoded + '''">''' + r1title + '''</a><br />nativeId: ''' + r1jobId + '''</div>')

            //Report 1 arrow
            var report1Arrow = svgContainer.append("polygon")
                                    .style("stroke-width", "1")
                                    .attr("points", "250,49, 150,49, 150,44, 140,50, 150,57, 150,51, 250,51");

            //Report 1 arrow name
            var report1ArrowName = svgContainer.append("text")
                                    .attr("x", 180)
                                    .attr("y", 10)
                                    .text("proms:reportingSystem")
                                    .style("font-family", "Verdana")
                                    .style("font-size", "smaller")
                                    .style("text-anchor", "middle");
            '''
            if len(reports['results']['bindings']) > 1:
                reports = reports['results']['bindings'][1:]
                i = 1
                for report in reports:
                    uri = report['r']['value']
                    title = report['t']['value']
                    jobId = report['job']['value']
                    reports_script += draw_report(i, uri, title, jobId, True)
                    i += 1
        else:
            #no reports
            reports_script = ''
    else:
        #we have a fault
        reports_script = '''
            var activityUsedFaultText = svgContainer.append('foreignObject')
                                .attr('x', 550)
                                .attr('y', 200)
                                .attr('width', 149)
                                .attr('height', 100)
                                .append("xhtml:body")
                                .html('<div style="width: 149px;">There is a fault with retrieving Activities that may have used this Entity</div>')
        '''
    return reports_script


def put_reportingsystem(reportingsystem_in_turtle):
    #replace the document's placeholder URI with one generated by this PROMS instance
    reportingsystem_in_turtle = replace_placeholder_uuids(reportingsystem_in_turtle)

    #try to make a graph of the input text
    g = Graph()
    try:
        g.parse(cStringIO.StringIO(reportingsystem_in_turtle), format="n3")
    except Exception as e:
        return [False, ['Could not parse input: ' + str(e)]]

    #conformance
    #from rulesets import proms_report
    conf_results = reportingsystems.ReportingSystems(g).get_result()
    #conf_results = proms_report.ReportingSystems(g).get_result()

    if conf_results['rule_results'][0]['passed']:
        result = functions_db.db_insert_secure(reportingsystem_in_turtle, True)
        if result[0]:
            return [True, 'OK']
        else:
            return [False, 'Error writing report to triplestore']
    else:
        return [False, conf_results['rule_results'][0]['fail_reasons']]


#
#   Reports
#
def get_reports_dict():
    query = '''
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT DISTINCT ?r ?t
        WHERE { GRAPH ?g {
          { ?r a proms:BasicReport . }
          UNION
          { ?r a proms:ExternalReport . }
          UNION
          { ?r a proms:InternalReport . }
          ?r rdf:label ?t
        } }
        ORDER BY ?r
    '''
    reports = functions_db.db_query_secure(query)

    report_items = []
    # Check if nothing is returned
    if reports and 'results' in reports:
        for report in reports['results']['bindings']:
            ret = {}
            ret['r'] = urllib.quote(str(report['r']['value']))
            ret['r_u'] = str(report['r']['value'])
            if report.get('t'):
                ret['t'] = str(report['t']['value'])
            report_items.append(ret)
    return report_items


def get_report(report_uri):
    query = '''
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?rt ?l ?id ?rs ?rs_t ?sac ?sac_t ?sat ?eac ?eac_t ?eat
        WHERE { GRAPH ?g {
          <''' + report_uri + '''> a ?rt .
          <''' + report_uri + '''> rdf:label ?l .
          <''' + report_uri + '''> proms:nativeId ?id .
          OPTIONAL { <''' + report_uri + '''> proms:reportingSystem ?rs .
          OPTIONAL { ?rs rdf:label ?rs_t . } }
          OPTIONAL { <''' + report_uri + '''> proms:startingActivity ?sac .
          ?sac prov:startedAtTime ?sat .
          ?sac rdf:label ?sac_t }
          OPTIONAL { <''' + report_uri + '''> proms:endingActivity ?eac .
          ?eac prov:endedAtTime ?eat .
          ?eac rdf:label ?eac_t }
        } }
    '''
    return functions_db.db_query_secure(query)


def get_report_dict(report_uri):
    report_detail = get_report(report_uri)
    ret = {}
    # Check this
    if report_detail and 'results' in report_detail:
        if len(report_detail['results']['bindings']) > 0:
            index = 0;
            if len(report_detail['results']['bindings']) > 1:
                index = 1;
            ret['l'] = report_detail['results']['bindings'][index]['l']['value']
            ret['t'] = report_detail['results']['bindings'][index]['rt']['value']
            if 'Basic' in ret['t']:
                ret['t_str'] = 'Basic'
            elif 'Internal' in ret['t']:
                ret['t_str'] = 'Internal'
            elif 'External' in ret['t']:
                ret['t_str'] = 'External'
            else:
                ret['t_str'] = 'Unknown Report Type'
            ret['id'] = report_detail['results']['bindings'][index]['id']['value']
            if('rs' in report_detail['results']['bindings'][0]):
                ret['rs'] = urllib.quote(report_detail['results']['bindings'][index]['rs']['value'])
                ret['rs_u'] = report_detail['results']['bindings'][index]['rs']['value']
            if('rs_t' in report_detail['results']['bindings'][0]):
                ret['rs_t'] = report_detail['results']['bindings'][index]['rs_t']['value']
            if('sat' in report_detail['results']['bindings'][0]):
                ret['sat'] = report_detail['results']['bindings'][index]['sat']['value']
            ret['uri'] = report_uri
            """
            svg_script = get_report_details_svg(report_uri)
            if svg_script[0] == True:
                ret['r_script'] = svg_script[1]
            """
    return ret


#TODO: Make sure needed
#TODO: get this query working
#TODO: get ordering by Report --> Activity --> startedAtTime
def get_reports_for_rs(reportingsystem_uri):
    query = '''
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?r ?t
        WHERE { GRAPH ?g {
          { ?r a proms:BasicReport . }
          UNION
          { ?r a proms:ExternalReport . }
          UNION
          { ?r a proms:InternalReport . }
          ?r rdf:label ?t .
          #?r proms:reportingSystem <''' + reportingsystem_uri + '''#> .
        } }
        ORDER BY ?r
    '''
    return functions_db.db_query_secure(query)


#TODO: Check if this is used
def get_report_metadata(report_uri):
    #TODO: landing page
    #get the report metadata from DB
    query = '''
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?rt ?t ?id ?rs ?rs_t ?sat
        WHERE { GRAPH ?g {
          <''' + report_uri + '''> a ?rt .
          <''' + report_uri + '''> rdf:label ?t .
          <''' + report_uri + '''> proms:nativeId ?id .
          <''' + report_uri + '''> proms:reportingSystem ?rs .
          ?rs rdf:label ?rs_t .
          <''' + report_uri + '''> proms:startingActivity ?sac .
          ?sac prov:startedAtTime ?sat .
        } }
    '''
    return functions_db.db_query_secure(query)


#TODO: draw Neighbours view for Report
def get_report_details_svg(report_uri):
    get_report_result = get_report(report_uri)
    if get_report_result and 'results' in get_report_result:
        if len(get_report_result['results']['bindings']) > 0:
            script = '''
                var svgContainer = d3.select("#container-content-2").append("svg")
                                                        .attr("width", 700)
                                                        .attr("height", 500);
            '''
            title = ''
            if get_report_result['results']['bindings'][0].get('l'):
                title = get_report_result['results']['bindings'][0]['l']['value']
            script += draw_report(1, None, title, None, False)

            sac = None;
            eac = None;
            if get_report_result['results']['bindings'][0].get('sac'):
                sac = get_report_result['results']['bindings'][0]['sac']['value']

            if get_report_result['results']['bindings'][0].get('eac'):
                eac = get_report_result['results']['bindings'][0]['sac']['value']

            if sac != eac:
                sac_title = "Starting Activity"
                if get_report_result['results']['bindings'][0].get('sac_t'):
                    sac_title = get_report_result['results']['bindings'][0]['sac_t']['value']
                script += draw_activity(1, 1, sac, sac_title)

                script += '''
                    var activityWGBArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "250,220, 160,220, 160,215, 150,221, 160,228, 160,222, 250,222");
                '''

                eac_title = "Ending Activity"
                if get_report_result['results']['bindings'][0].get('eac_t'):
                    eac_title = get_report_result['results']['bindings'][0]['eac_t']['value']
                script += draw_activity(2, 1, sac, eac_title)

            else:
                sac_title = "Activity"
                if get_report_result['results']['bindings'][0].get('sac_t'):
                    sac_title = get_report_result['results']['bindings'][0]['sac_t']['value']
                script += draw_activity(1, 1, sac, sac_title)

                script += '''
                    var activityWGBArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "250,200, 160,200, 160,195, 150,201, 160,208, 160,202, 250,202");
                '''

            return [True, script]

        else:
            return [False, 'Not found']
    else:
        return [False, 'There was a fault']


# XXX XXX XXX
def get_report_activity_wgb_svg(entity_uri):
    script = ''
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?a ?t
        WHERE { GRAPH ?g {
          ?a prov:generated <''' + entity_uri + '''> .
          ?a rdf:label ?t .
        } }
    '''
    entity_results = functions_db.db_query_secure(query)

    if entity_results and 'results' in entity_results:
        wgb = entity_results['results']['bindings']
        if len(wgb) == 1:
            if wgb[0].get('t'):
                title = wgb[0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wgb[0]['a']['value'])

            script += '''
                //Activity (wasGeneratedBy)
                var activityWGB = svgContainer.append("rect")
                                        .attr("x", 1)
                                        .attr("y", 200)
                                        .attr("width", 150)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                //Activity class name
                var activityWGBName = svgContainer.append("text")
                                        .attr("x", 75)
                                        .attr("y", 230)
                                        .text("Activity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Activity (wasGeneratedBy) arrow
                var activityWGBArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "250,249, 160,249, 160,244, 150,250, 160,257, 160,251, 250,251");

                //Activity (wasGeneratedBy) arrow name
                var activityUsedArrowName = svgContainer.append("text")
                                        .attr("x", 200)
                                        .attr("y", 195)
                                        .text("prov:wasGeneratedBy")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Activity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#cfceff;">' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/activity/?uri=''' + uri_encoded + '''">' +
                            '         ''' + title + '''' +
                            '     </a>' +
                            '</div>';
                var activityTitle = svgContainer.append('foreignObject')
                                .attr('x', 2)
                                .attr('y', 240)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        else:
            pass

    return script


#TODO: remove hash from URI rewrite
def put_report(report_in_turtle):
    #replace the document's placeholder URI with one generated by this PROMS instance
    report_in_turtle = replace_placeholder_uuids(report_in_turtle)

    #try to make a graph of the input text
    g = Graph()
    try:
        g.parse(cStringIO.StringIO(report_in_turtle), format="n3")
    except Exception as e:
        return [False, ['Could not parse input: ' + str(e)]]

    #conformance
    conf_results = proms.PromsReport(g).get_result()
    #conf_results = proms_report.PromsReport(g).get_result()

    if conf_results['rule_results'][0]['passed']:
        #Get Report URI
        query = '''
            PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX proms: <http://promsns.org/def/proms#>
            SELECT  ?r ?job
            WHERE {
              {?r a proms:Report}
              UNION
              {?r a proms:BasicReport}
              UNION
              {?r a proms:ExternalReport}
              UNION
              {?r a proms:InternalReport}
              ?r proms:nativeId ?job .
            }
        '''
        r_uri = ''
        r_nid = ''
        graph_name = ''
        qres = g.query(query)
        for row in qres:
            r_uri = row[0]
            r_nid = row[1]
            break
        if r_uri and r_nid:
            graph_name = '<' + r_uri + '>'
        result = functions_db.db_insert_secure_named_graph(report_in_turtle, graph_name, True)
        if result[0]:
            return [True, 'OK']
        else:
            return [False, 'Error writing report to triplestore']
    else:
        return [False, conf_results['rule_results'][0]['fail_reasons']]

#
#   Entities
#
def get_entities_dict():
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?e ?l ?t
        WHERE { GRAPH ?g {
          { ?e rdf:label ?l . }
          { ?e a prov:Entity . }
          UNION
          { ?e a prov:Plan . }
          OPTIONAL { ?s rdf:label ?t . }
        } }
        ORDER BY ?e
    '''
    entities = functions_db.db_query_secure(query)
    entity_items = []
    # Check if nothing is returned
    if entities and 'results' in entities:
        for entity in entities['results']['bindings']:
            ret = {}
            ret['e'] = urllib.quote(str(entity['e']['value']))
            ret['e_u'] = str(entity['e']['value'])
            if entity.get('l'):
                ret['l'] = str(entity['l']['value'])
            entity_items.append(ret)
    return entity_items


def get_entity(entity_uri):
    #TODO: landing page with view options:
    #   wasDerivedFrom, wasGeneratedBy, inv. used, hadPrimarySource, wasAttributedTo, value
    #get the report metadata from DB
    query = '''
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT DISTINCT ?l ?c ?dl ?t ?v ?wat ?wat_name
        WHERE { GRAPH ?g {
            OPTIONAL { <''' + entity_uri + '''> rdf:label ?l . }
            OPTIONAL { <''' + entity_uri + '''> dc:created ?c . }
            OPTIONAL { <''' + entity_uri + '''> dcat:downloadURL ?dl . }
            { <''' + entity_uri + '''> a prov:Entity . }
            UNION
            { <''' + entity_uri + '''> a prov:Plan . }
            OPTIONAL { <''' + entity_uri + '''> rdf:label ?t . }
            OPTIONAL { <''' + entity_uri + '''> prov:value ?v . }
            OPTIONAL { <''' + entity_uri + '''> prov:wasAttributedTo ?wat . }
            OPTIONAL { ?wat foaf:name ?wat_name . }
        } }
    '''
    return functions_db.db_query_secure(query)


def get_entity_dict(entity_uri):
    entity_detail = get_entity(entity_uri)
    ret = {}
    if entity_detail and 'results' in entity_detail:
        if len(entity_detail['results']['bindings']) > 0:
            if('l' in entity_detail['results']['bindings'][0]):
                ret['l'] = entity_detail['results']['bindings'][0]['l']['value']
            if('c' in entity_detail['results']['bindings'][0]):
                ret['c'] = entity_detail['results']['bindings'][0]['c']['value']
            if('dl' in entity_detail['results']['bindings'][0]):
                ret['dl'] = entity_detail['results']['bindings'][0]['dl']['value']
            if('t' in entity_detail['results']['bindings'][0]):
                ret['t'] = entity_detail['results']['bindings'][0]['t']['value']
            if('v' in entity_detail['results']['bindings'][0]):
                ret['v'] = entity_detail['results']['bindings'][0]['v']['value']
            if('wat' in entity_detail['results']['bindings'][0]):
                ret['wat'] = entity_detail['results']['bindings'][0]['wat']['value']
            if('wat_name' in entity_detail['results']['bindings'][0]):
                ret['wat_name'] = entity_detail['results']['bindings'][0]['wat_name']['value']
            svg_script = get_entity_details_svg(entity_uri)
            if svg_script[0] == True:
                e_script = svg_script[1]
                e_script += get_entity_activity_wgb_svg(entity_uri)
                e_script += get_entity_activity_used_svg(entity_uri)
                e_script += get_entity_entity_wdf_svg(entity_uri)
                ret['e_script'] = e_script
            ret['uri'] = entity_uri
    return ret


def get_entity_details_svg(entity_uri):
    get_entity_result = get_entity(entity_uri)
    #check for any faults
    if get_entity_result and 'results' in get_entity_result:
        if len(get_entity_result['results']['bindings']) > 0:
            script = '''
                    var svgContainer = d3.select("#container-content-2").append("svg")
                                                        .attr("width", 700)
                                                        .attr("height", 500);

                    //Entity
                    var entity = svgContainer.append("ellipse")
                                            .attr("cx", 350)
                                            .attr("cy", 250)
                                            .attr("rx", 100)
                                            .attr("ry", 65)
                                            .attr("fill", "#ffffbe")
                                            .attr("stroke", "grey")
                                            .attr("stroke-width", "1");

                    //Entity class name
                    var entityName = svgContainer.append("text")
                                            .attr("x", 350)
                                            .attr("y", 230)
                                            .text("Entity")
                                            .style("font-family", "Verdana")
                                            .style("text-anchor", "middle");
            '''
            #print its title, if it has one
            if get_entity_result['results']['bindings'][0].get('t'):
                title = get_entity_result['results']['bindings'][0]['t']['value']
                script += '''
                    //Entity title
                    if(navigator.appName != "Microsoft Internet Explorer")
                        var entityTitle = svgContainer.append('foreignObject')
                                            .attr('x', 275)
                                            .attr('y', 250)
                                            .attr('width', 149)
                                            .attr('height', 100)
                                            .append("xhtml:body")
                                            .html('<div style="width: 149px; font-size:smaller; background-color:#ffffbe;">''' + title + '''</div>');
                    else
                        var entityTitle = svgContainer.append("text")
                                            .attr("x", 350)
                                            .attr("y", 260)
                                            .text("''' + title + '''")
                                            .style("font-family", "Verdana")
                                            .style("font-size", "12px")
                                            .style("text-anchor", "middle");
                '''
            #print its value, if it has one
            if get_entity_result['results']['bindings'][0].get('v'):
                value = get_entity_result['results']['bindings'][0]['v']['value']
                script += '''
                    //value
                    var value = svgContainer.append("rect")
                                            .attr("x", 1)
                                            .attr("y", 400)
                                            .attr("width", 150)
                                            .attr("height", 99)
                                            .attr("fill", "none")
                                            .attr("stroke", "grey")
                                            .attr("stroke-width", "1");

                    //value property name
                    var entityTitle = svgContainer.append('foreignObject')
                                            .attr('x', 2)
                                            .attr('y', 401)
                                            .attr('width', 148)
                                            .attr('height', 98)
                                            .append("xhtml:body")
                                            .html('<div style="width: 149px; font-size:smaller; background-color:white; overflow:hidden;">''' + value + '''</div>');

                    //value property arrow
                    var valueArrow = svgContainer.append("polygon")
                                            .style("stroke-width", "1")
                                            .style("stroke", "grey")
                                            .attr("fill", "grey")
                                            .attr("points", "148,400 265,285, 263,288, 150,400, 155,400, 150,392");

                    //value property arrow name
                    var valueArrowName = svgContainer.append("text")
                                            .attr("x", 150)
                                            .attr("y", 350)
                                            .text("prov:value")
                                            .style("font-family", "Verdana")
                                            .style("font-size", "smaller")
                                            .style("text-anchor", "middle");
                '''

            #print its Agent, if it has one
            if get_entity_result['results']['bindings'][0].get('wat'):
                agent_uri = get_entity_result['results']['bindings'][0]['wat']['value']
                agent_uri_encoded = urllib.quote(agent_uri)
                if get_entity_result['results']['bindings'][0].get('wat_name'):
                    agent_name = get_entity_result['results']['bindings'][0]['wat_name']['value']
                else:
                    agent_name = agent_uri.split('#')
                    if len(agent_name) < 2:
                        agent_name = agent_uri.split('/')
                    agent_name = agent_name[-1]

                script += '''
                    //Agent (wasAttributedTo)
                    var agent = svgContainer.append("polygon")
                                            .style("stroke", "black")
                                            .style("fill", "moccasin")
                                            .style("stroke-width", "1")
                                            .attr("points", "350,1, 435,25, 435,100, 265,100, 265,25");

                    //Agent class name
                    var agentName = svgContainer.append("text")
                                            .attr("x", 350)
                                            .attr("y", 40)
                                            .text("Agent")
                                            .style("font-family", "Verdana")
                                            .style("text-anchor", "middle");

                    //Agent (wasAttributedTo) arrow
                    var agentArrow = svgContainer.append("polygon")
                                            .style("stroke-width", "1")
                                            .attr("points", "349,185, 349,110, 344,110, 350,100, 356,110, 351,110, 351,185");

                    //Agent (wasAttributedTo) arrow name
                    var agentArrowName = svgContainer.append("text")
                                            .attr("x", 350)
                                            .attr("y", 150)
                                            .text("prov:wasAttributedTo")
                                            .style("font-family", "Verdana")
                                            .style("font-size", "smaller")
                                            .style("text-anchor", "middle");

                    //Agent name or URI
                    var entityTitle = svgContainer.append('foreignObject')
                                            .attr('x', 277)
                                            .attr('y', 60)
                                            .attr('width', 148)
                                            .attr('height', 98)
                                            .append("xhtml:body")
                                            .html('<div style="width: 149px; font-size:smaller; background-color:moccasin; overflow:hidden;"><a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/agent/?uri=''' + agent_uri_encoded + '''">''' + agent_name + '''</a></div>')
                '''
            return [True, script]
        else:
            return [False, 'Not found']
    else:
        return [False, 'There was a fault']


def get_entity_activity_wgb_svg(entity_uri):
    script = ''
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?a ?t
        WHERE { GRAPH ?g {
          ?a prov:generated <''' + entity_uri + '''> .
          ?a rdf:label ?t .
        } }
    '''
    entity_results = functions_db.db_query_secure(query)

    if entity_results and 'results' in entity_results:
        wgb = entity_results['results']['bindings']
        if len(wgb) == 1:
            if wgb[0].get('t'):
                title = wgb[0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wgb[0]['a']['value'])

            script += '''
                //Activity (wasGeneratedBy)
                var activityWGB = svgContainer.append("rect")
                                        .attr("x", 1)
                                        .attr("y", 200)
                                        .attr("width", 150)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                //Activity class name
                var activityWGBName = svgContainer.append("text")
                                        .attr("x", 75)
                                        .attr("y", 230)
                                        .text("Activity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Activity (wasGeneratedBy) arrow
                var activityWGBArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "250,249, 160,249, 160,244, 150,250, 160,257, 160,251, 250,251");

                //Activity (wasGeneratedBy) arrow name
                var activityUsedArrowName = svgContainer.append("text")
                                        .attr("x", 200)
                                        .attr("y", 195)
                                        .text("prov:wasGeneratedBy")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Activity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#cfceff;">' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/activity/?uri=''' + uri_encoded + '''">' +
                            '         ''' + title + '''' +
                            '     </a>' +
                            '</div>';
                var activityTitle = svgContainer.append('foreignObject')
                                .attr('x', 2)
                                .attr('y', 240)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        else:
            pass

    return script


def get_entity_activity_used_svg(entity_uri):
    script = ''
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?a ?t
        WHERE { GRAPH ?g {
          ?a prov:used <''' + entity_uri + '''> .
          ?a rdf:label ?t .
        } }
    '''
    entity_result = functions_db.db_query_secure(query)

    if entity_result and 'results' in entity_result:
        used = entity_result['results']['bindings']
        if len(used) == 1:
            if used[0].get('t'):
                title = used[0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(used[0]['a']['value'])

            script += '''
                //Activity (used)
                var activityUsed = svgContainer.append("rect")
                                        .attr("x", 550)
                                        .attr("y", 200)
                                        .attr("width", 149)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                //Activity class name
                var activityUsedName = svgContainer.append("text")
                                        .attr("x", 625)
                                        .attr("y", 230)
                                        .text("Activity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Activity (used) arrow
                var activityUsedArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "550,249, 460,249, 460,244, 450,250, 460,257, 460,251, 550,251");

                //Activity (used) arrow name
                var activityUsedArrowName = svgContainer.append("text")
                                        .attr("x", 500)
                                        .attr("y", 240)
                                        .text("prov:used")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Activity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#cfceff;">' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/activity/?uri=''' + uri_encoded + '''">' +
                            '         ''' + title + '''' +
                            '     </a>' +
                            '</div>';
                var activityTitle = svgContainer.append('foreignObject')
                                .attr('x', 551)
                                .attr('y', 240)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        elif len(used) > 1:
            script += '''
                //Activity (used) multiple
                var activityUsed1 = svgContainer.append("rect")
                                        .attr("x", 550)
                                        .attr("y", 200)
                                        .attr("width", 149)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                var activityUsed2 = svgContainer.append("rect")
                                        .attr("x", 545)
                                        .attr("y", 195)
                                        .attr("width", 149)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                var activityUsedN = svgContainer.append("rect")
                                        .attr("x", 540)
                                        .attr("y", 190)
                                        .attr("width", 149)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                //Activit(y|ies) class name
                var activityUsedName = svgContainer.append("text")
                                        .attr("x", 625)
                                        .attr("y", 220)
                                        .text("Activity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Activity (used) arrow
                var activityUsedArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "540,249, 460,249, 460,244, 450,250, 460,257, 460,251, 540,251");

                //Activity (used) arrow name
                var activityUsedArrowName = svgContainer.append("text")
                                        .attr("x", 500)
                                        .attr("y", 240)
                                        .text("prov:used")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Activity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#cfceff;">' +
                            '   Multiple Activities, click ' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''function/sparql/">here</a> ' +
                            '   to search' +
                            '</div>';
                var activityTitle = svgContainer.append('foreignObject')
                                .attr('x', 541)
                                .attr('y', 240)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        else:
            #do nothing as no Activities found
            pass
    else:
        #we have a fault
        script += '''
            var activityUsedFaultText = svgContainer.append('foreignObject')
                                    .attr('x', 550)
                                    .attr('y', 200)
                                    .attr('width', 149)
                                    .attr('height', 100)
                                    .append("xhtml:body")
                                    .html('<div style="width: 149px;">There is a fault with retrieving Activities that may have used this Entity</div>')
        '''

    return script


#TODO: multiple Entity SPARQL
def get_entity_entity_wdf_svg(entity_uri):
    script = ''
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?e ?t
        WHERE { GRAPH ?g {
            { <''' + entity_uri + '''> a prov:Entity . }
            UNION
            { <''' + entity_uri + '''> a prov:Plan . }
            <''' + entity_uri + '''> prov:wasDerivedFrom ?e .
            ?e rdf:label ?t .
        } }
    '''
    entity_results = functions_db.db_query_secure(query)

    if entity_results and 'results' in entity_results:
        wdf = entity_results['results']['bindings']
        if len(wdf) == 1:
            if wdf[0].get('t'):
                title = wdf[0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wdf[0]['e']['value'])
            script += '''
                //Entity (wasDerivedFrom)
                var entityWDF = svgContainer.append("ellipse")
                                        .attr("cx", 350)
                                        .attr("cy", 435)
                                        .attr("rx", 100)
                                        .attr("ry", 64)
                                        .attr("fill", "#ffffbe")
                                        .attr("stroke", "grey")
                                        .attr("stroke-width", "1");

                //Entity class name
                var entityWDFName = svgContainer.append("text")
                                        .attr("x", 350)
                                        .attr("y", 420)
                                        .text("Entity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Entity (wasDerivedFrom) arrow
                var entityWDFArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "349,315, 349,360, 344,360, 350,370, 356,360, 351,360, 351,315");

                //Entity (wasDerivedFrom) arrow name
                var entityWDFArrowName = svgContainer.append("text")
                                        .attr("x", 350)
                                        .attr("y", 350)
                                        .text("prov:wasDerivedFrom")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Activity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity/?uri=''' + uri_encoded + '''">' +
                            '         ''' + title + '''' +
                            '     </a>' +
                            '</div>';
                var entityTitle = svgContainer.append('foreignObject')
                                .attr('x', 275)
                                .attr('y', 435)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        elif len(wdf) > 1:
            script += '''
                //Activity (used) multiple
                var entityWdf1 = svgContainer.append("ellipse")
                                        .attr("cx", 350)
                                        .attr("cy", 435)
                                        .attr("rx", 100)
                                        .attr("ry", 64)
                                        .attr("fill", "#ffffbe")
                                        .attr("stroke", "grey")
                                        .attr("stroke-width", "1");

                var entityWdf2 = svgContainer.append("ellipse")
                                        .attr("cx", 345)
                                        .attr("cy", 430)
                                        .attr("rx", 100)
                                        .attr("ry", 64)
                                        .attr("fill", "#ffffbe")
                                        .attr("stroke", "grey")
                                        .attr("stroke-width", "1");

                var entityWdfN = svgContainer.append("ellipse")
                                        .attr("cx", 340)
                                        .attr("cy", 425)
                                        .attr("rx", 100)
                                        .attr("ry", 64)
                                        .attr("fill", "#ffffbe")
                                        .attr("stroke", "grey")
                                        .attr("stroke-width", "1");

                //Entit(y|ies) class name
                var entityWDFName = svgContainer.append("text")
                                        .attr("x", 340)
                                        .attr("y", 400)
                                        .text("Entity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Entity (wasDerivedFrom) arrow
                var entityWDFArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "349,315, 349,350, 344,350, 350,360, 356,350, 351,350, 351,315");

                //Entity (wasDerivedFrom) arrow name
                var entityWDFArrowName = svgContainer.append("text")
                                        .attr("x", 350)
                                        .attr("y", 340)
                                        .text("prov:wasDerivedFrom")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Entity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                            '   Multiple Entities, click ' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''function/sparql/">here</a> ' +
                            '   to search' +
                            '</div>';
                var entityTitle = svgContainer.append('foreignObject')
                                .attr('x', 275)
                                .attr('y', 425)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        else:
            #do nothing as no Activities found
            pass
    else:
        #we have a fault
        script += '''
            var activityUsedFaultText = svgContainer.append('foreignObject')
                                    .attr('x', 550)
                                    .attr('y', 200)
                                    .attr('width', 149)
                                    .attr('height', 100)
                                    .append("xhtml:body")
                                    .html('<div style="width: 149px;">There is a fault with retrieving Activities that may have used this Entity</div>')
        '''

    return script


#
#   Activities
#
def get_activities_dict():
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?a ?l
        WHERE { GRAPH ?g {
          ?a a prov:Activity .
          ?a rdf:label ?l
        } }
        ORDER BY ?a
    '''
    activities = functions_db.db_query_secure(query)
    activity_items = []
    if activities and 'results' in activities:
        for activity in activities['results']['bindings']:
            ret = {}
            ret['a'] = urllib.quote(str(activity['a']['value']))
            ret['a_u'] = str(activity['a']['value'])
            if activity.get('l'):
                ret['l'] = str(activity['l']['value'])
            activity_items.append(ret)
    return activity_items


def get_activity(activity_uri):
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT DISTINCT ?l ?t ?sat ?eat ?waw ?r ?rt
        WHERE { GRAPH ?g {
          <''' + activity_uri + '''> a prov:Activity .
          <''' + activity_uri + '''> rdf:label ?l .
          { ?r proms:startingActivity <''' + activity_uri + '''> . }
          UNION
          { ?r proms:endingActivity <''' + activity_uri + '''> . }
          OPTIONAL { ?r rdf:label ?rt . }
          OPTIONAL { <''' + activity_uri + '''> rdf:label ?t . }
          OPTIONAL { <''' + activity_uri + '''> prov:startedAtTime ?sat . }
          OPTIONAL { <''' + activity_uri + '''> prov:endedAtTime ?eat . }
          OPTIONAL { <''' + activity_uri + '''> prov:wasAssociatedWith ?waw . }
          OPTIONAL { ?waw foaf:name ?waw_name . }
        } }
    '''
    return functions_db.db_query_secure(query)


def get_activity_dict(activity_uri):
    activity_detail = get_activity(activity_uri)
    ret = {}
    if activity_detail and 'results' in activity_detail:
        if len(activity_detail['results']['bindings']) > 0:
            ret['l'] = activity_detail['results']['bindings'][0]['l']['value']
            if 't' in activity_detail['results']['bindings'][0]:
                ret['t'] = activity_detail['results']['bindings'][0]['t']['value']
            if 'sat' in activity_detail['results']['bindings'][0]:
                ret['sat'] = activity_detail['results']['bindings'][0]['sat']['value']
            if 'eat' in activity_detail['results']['bindings'][0]:
                ret['eat'] = activity_detail['results']['bindings'][0]['eat']['value']
            if 'waw' in activity_detail['results']['bindings'][0]:
                ret['waw'] = activity_detail['results']['bindings'][0]['waw']['value']
            if 'waw_name' in activity_detail['results']['bindings'][0]:
                ret['waw_name'] = activity_detail['results']['bindings'][0]['waw_name']['value']
            if 'r' in activity_detail['results']['bindings'][0]:
                ret['r'] = urllib.quote(activity_detail['results']['bindings'][0]['r']['value'])
                ret['r_u'] = activity_detail['results']['bindings'][0]['r']['value']
            if 'rt' in activity_detail['results']['bindings'][0]:
                ret['rt'] = activity_detail['results']['bindings'][0]['rt']['value']
            svg_script = get_activity_details_svg(activity_uri)
            if svg_script[0] == True:
                a_script = svg_script[1]
                a_script += get_activity_used_entities_svg(activity_uri)
                a_script += get_activity_generated_entities_svg(activity_uri)
                a_script += get_activity_was_informed_by(activity_uri)
                ret['a_script'] = a_script
            ret['uri'] = activity_uri
    return ret


# TODO: X position is different depending on how it's used by Entity or Report
def draw_activity(n, x, uri, title):
    yOffset = n * 130 + 15
    svg = '''
            //Activity (wasGeneratedBy)
            var activityWGB = svgContainer.append("rect")
                                    .attr("x", ''' + str(x) + ''')
                                    .attr("y", ''' + str(yOffset) + ''')
                                    .attr("width", 150)
                                    .attr("height", 100)
                                    .attr("fill", "#cfceff")
                                    .attr("stroke", "blue")
                                    .attr("stroke-width", "1");

            //Activity class name
            var activityWGBName = svgContainer.append("text")
                                    .attr("x", ''' + str(x + 74) + ''')
                                    .attr("y", '''+ str(yOffset + 30) + ''')
                                    .text("Activity")
                                    .style("font-family", "Verdana")
                                    .style("text-anchor", "middle");
    '''

    if uri:
        uri_encoded = urllib.quote(uri)
        svg += '''
            //Activity title
            title_html = '<div style="width: 147px; font-size:smaller; background-color:#cfceff;">' +
                        '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/activity/?uri=''' + uri_encoded + '''">' +
                        '         ''' + title + '''' +
                        '     </a>' +
                        '</div>';
            var activityTitle = svgContainer.append('foreignObject')
                            .attr('x', ''' + str(x + 1) + ''')
                            .attr('y', ''' + str(yOffset + 50) + ''')
                            .attr('width', 147)
                            .attr('height', 60)
                            .append("xhtml:body")
                            .html(title_html);
        '''
    else:
        svg += '''
            //Activity title
            var activityTitle = svgContainer.append('foreignObject')
                                    .attr('x', ''' + str(x) + ''')
                                    .attr('y', ''' + str(yOffset + 50) + ''')
                                    .attr('width', 148)
                                    .attr('height', 100)
                                    .append("xhtml:body")
                                    .html('<div style="width: 149px; font-size:smaller; background-color:#cfceff;">''' + title + '''</div>')
        '''

    return svg;


def get_activity_details_svg(activity_uri):
    get_activity_result = get_activity(activity_uri)
    #check for any faults
    if get_activity_result and 'results' in get_activity_result:
        #activity_details = json.loads(get_activity_result[1])
        #check we got a result
        if len(get_activity_result['results']['bindings']) > 0:
            script = '''
                    var svgContainer = d3.select("#container-content-2").append("svg")
                                                        .attr("width", 700)
                                                        .attr("height", 500);

                    //Activity
                    var activityWGB = svgContainer.append("rect")
                                        .attr("x", 275)
                                        .attr("y", 200)
                                        .attr("width", 150)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                    //Activity class name
                    var activityName = svgContainer.append("text")
                                            .attr("x", 350)
                                            .attr("y", 230)
                                            .text("Activity")
                                            .style("font-family", "Verdana")
                                            .style("text-anchor", "middle");
            '''
            #print its title, if it has one
            if get_activity_result['results']['bindings'][0].get('t'):
                title = get_activity_result['results']['bindings'][0]['t']['value']
                script += '''
                    //Activity title
                    var activityTitle = svgContainer.append('foreignObject')
                                            .attr('x', 276)
                                            .attr('y', 250)
                                            .attr('width', 148)
                                            .attr('height', 100)
                                            .append("xhtml:body")
                                            .html('<div style="width: 149px; font-size:smaller; background-color:#cfceff;">''' + title + '''</div>')
                '''

            #print its Agent, if it has one
            if get_activity_result['results']['bindings'][0].get('waw'):
                agent_uri = get_activity_result['results']['bindings'][0]['waw']['value']
                agent_uri_encoded = urllib.quote(agent_uri)
                if get_activity_result['results']['bindings'][0].get('waw_name'):
                    agent_name = get_activity_result['results']['bindings'][0]['waw_name']['value']
                else:
                    agent_name = agent_uri.split('#')
                    if len(agent_name) < 2:
                        agent_name = agent_uri.split('/')
                    agent_name = agent_name[-1]

                script += '''
                    //Agent (wasAttributedTo)
                    var agent = svgContainer.append("polygon")
                                            .style("stroke", "black")
                                            .style("fill", "moccasin")
                                            .style("stroke-width", "1")
                                            .attr("points", "350,1, 435,25, 435,100, 265,100, 265,25");

                    //Agent class name
                    var agentName = svgContainer.append("text")
                                            .attr("x", 350)
                                            .attr("y", 40)
                                            .text("Agent")
                                            .style("font-family", "Verdana")
                                            .style("text-anchor", "middle");

                    //Agent (wasAttributedTo) arrow
                    var agentArrow = svgContainer.append("polygon")
                                            .style("stroke-width", "1")
                                            .attr("points", "349,199, 349,110, 344,110, 350,100, 356,110, 351,110, 351,199");

                    //Agent (wasAttributedTo) arrow name
                    var agentArrowName = svgContainer.append("text")
                                            .attr("x", 350)
                                            .attr("y", 150)
                                            .text("prov:wasAssociatedWith")
                                            .style("font-family", "Verdana")
                                            .style("font-size", "smaller")
                                            .style("text-anchor", "middle");

                    //Agent name or URI
                    var entityTitle = svgContainer.append('foreignObject')
                                            .attr('x', 277)
                                            .attr('y', 60)
                                            .attr('width', 148)
                                            .attr('height', 98)
                                            .append("xhtml:body")
                                            .html('<div style="width: 149px; font-size:smaller; background-color:moccasin; overflow:hidden;"><a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/agent/?uri=''' + agent_uri_encoded + '''">''' + agent_name + '''</a></div>')
                '''
            return [True, script]
        else:
            return [False, 'Not found']
    else:
        return [False, 'There was a fault']


#TODO: multiple Entity SPARQL
def get_activity_used_entities_svg(activity_uri):
    script = ''
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT *
        WHERE { GRAPH ?g {
          <''' + activity_uri + '''> prov:used ?u .
          OPTIONAL {?u rdf:label ?t .}
        } }
    '''
    activity_results = functions_db.db_query_secure(query)
    if activity_results and 'results' in activity_results:
        #used = json.loads(activity_results[1])['results']
        used = activity_results['results']
        if len(used['bindings']) > 0:
            if used['bindings'][0].get('t'):
                title = used['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(used['bindings'][0]['u']['value'])

            script += '''
                //Entity (used)
                var entityUsed = svgContainer.append("ellipse")
                                        .attr("cx", 101)
                                        .attr("cy", 250)
                                        .attr("rx", 100)
                                        .attr("ry", 64)
                                        .attr("fill", "#ffffbe")
                                        .attr("stroke", "grey")
                                        .attr("stroke-width", "1");

                //Entity class name
                var entityUsedName = svgContainer.append("text")
                                        .attr("x", 101)
                                        .attr("y", 230)
                                        .text("Entity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Entity (used) arrow
                var entityUsedArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "275,249, 211,249, 211,244, 201,250, 211,257, 211,251, 275,251");

                //Entity (used) arrow name
                var entityUsedArrowName = svgContainer.append("text")
                                        .attr("x", 235)
                                        .attr("y", 240)
                                        .text("prov:used")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Entity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity/?uri=''' + uri_encoded + '''">' +
                            '         ''' + title + '''' +
                            '     </a>' +
                            '</div>';
                var entityUsedTitle = svgContainer.append('foreignObject')
                                .attr('x', 25)
                                .attr('y', 250)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
            if len(used['bindings']) > 1:
                if used['bindings'][1].get('t'):
                    title = used['bindings'][1]['t']['value']
                else:
                    title = 'uri'
                uri_encoded = urllib.quote(used['bindings'][1]['u']['value'])

                script += '''
                    //Entity (used)
                    var entityUsed = svgContainer.append("ellipse")
                                            .attr("cx", 101)
                                            .attr("cy", 100)
                                            .attr("rx", 100)
                                            .attr("ry", 64)
                                            .attr("fill", "#ffffbe")
                                            .attr("stroke", "grey")
                                            .attr("stroke-width", "1");

                    //Entity class name
                    var entityUsedName = svgContainer.append("text")
                                            .attr("x", 101)
                                            .attr("y", 80)
                                            .text("Entity")
                                            .style("font-family", "Verdana")
                                            .style("text-anchor", "middle");

                    //Entity (used) arrow
                    var entityUsedArrow = svgContainer.append("polygon")
                                            .style("stroke-width", "1")
                                            .attr("points", "275,249, 180,150, 176,153, 176,142, 186,144, 182,148, 275,247");

                    //Entity title
                    title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                                '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity/?uri=''' + uri_encoded + '''">' +
                                '         ''' + title + '''' +
                                '     </a>' +
                                '</div>';
                    var entityUsedTitle = svgContainer.append('foreignObject')
                                    .attr('x', 25)
                                    .attr('y', 100)
                                    .attr('width', 147)
                                    .attr('height', 60)
                                    .append("xhtml:body")
                                    .html(title_html);
                '''
                if len(used['bindings']) == 3:
                    if used['bindings'][2].get('t'):
                        title = used['bindings'][2]['t']['value']
                    else:
                        title = 'uri'
                    uri_encoded = urllib.quote(used['bindings'][2]['u']['value'])

                    script += '''
                        //Entity (used)
                        var entityUsed = svgContainer.append("ellipse")
                                                .attr("cx", 101)
                                                .attr("cy", 400)
                                                .attr("rx", 100)
                                                .attr("ry", 64)
                                                .attr("fill", "#ffffbe")
                                                .attr("stroke", "grey")
                                                .attr("stroke-width", "1");

                        //Entity class name
                        var entityUsedName = svgContainer.append("text")
                                                .attr("x", 101)
                                                .attr("y", 380)
                                                .text("Entity")
                                                .style("font-family", "Verdana")
                                                .style("text-anchor", "middle");

                        //Entity (used) arrow
                        var entityUsedArrow = svgContainer.append("polygon")
                                                .style("stroke-width", "1")
                                                .attr("points", "275,251, 180,350, 176,347, 176,358, 186,356, 182,352, 275,253");

                        //Entity title
                        title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                                    '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity/?uri=''' + uri_encoded + '''">' +
                                    '         ''' + title + '''' +
                                    '     </a>' +
                                    '</div>';
                        var entityUsedTitle = svgContainer.append('foreignObject')
                                        .attr('x', 25)
                                        .attr('y', 400)
                                        .attr('width', 147)
                                        .attr('height', 60)
                                        .append("xhtml:body")
                                        .html(title_html);
                    '''
                elif len(used['bindings']) > 3:
                    # < 3
                    script = ''  # reset script
                    script += '''
                        //Entity (used)
                        var entityUsed1 = svgContainer.append("ellipse")
                                                .attr("cx", 101)
                                                .attr("cy", 250)
                                                .attr("rx", 100)
                                                .attr("ry", 64)
                                                .attr("fill", "#ffffbe")
                                                .attr("stroke", "grey")
                                                .attr("stroke-width", "1");

                        var entityUsed2 = svgContainer.append("ellipse")
                                                .attr("cx", 106)
                                                .attr("cy", 255)
                                                .attr("rx", 100)
                                                .attr("ry", 64)
                                                .attr("fill", "#ffffbe")
                                                .attr("stroke", "grey")
                                                .attr("stroke-width", "1");

                        var entityUsedN = svgContainer.append("ellipse")
                                                .attr("cx", 111)
                                                .attr("cy", 260)
                                                .attr("rx", 100)
                                                .attr("ry", 64)
                                                .attr("fill", "#ffffbe")
                                                .attr("stroke", "grey")
                                                .attr("stroke-width", "1");

                        //Entity class name
                        var entityUsedName = svgContainer.append("text")
                                                .attr("x", 111)
                                                .attr("y", 240)
                                                .text("Entity")
                                                .style("font-family", "Verdana")
                                                .style("text-anchor", "middle");

                        //Entity (used) arrow
                        var entityUsedArrow = svgContainer.append("polygon")
                                                .style("stroke-width", "1")
                                                .attr("points", "275,249, 221,249, 221,244, 211,250, 221,257, 221,251, 275,251");

                        //Entity (used) arrow name
                        var entityUsedArrowName = svgContainer.append("text")
                                                .attr("x", 235)
                                                .attr("y", 240)
                                                .text("prov:used")
                                                .style("font-family", "Verdana")
                                                .style("font-size", "smaller")
                                                .style("text-anchor", "middle");

                        //Entity title
                        title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                                    '   Multiple Entities, click ' +
                                    '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''function/sparql/">here</a> ' +
                                    '   to search' +
                                    '</div>';
                        var entityUsedTitle = svgContainer.append('foreignObject')
                                        .attr('x', 35)
                                        .attr('y', 250)
                                        .attr('width', 147)
                                        .attr('height', 60)
                                        .append("xhtml:body")
                                        .html(title_html);
                    '''
        else:
            # zero
            pass
    else:
        #we have a fault
        script += '''
            var entityUsedFaultText = svgContainer.append('foreignObject')
                                    .attr('x', 1)
                                    .attr('y', 200)
                                    .attr('width', 149)
                                    .attr('height', 100)
                                    .append("xhtml:body")
                                    .html('<div style="width: 149px;">There is a fault with retrieving Entities that may have been used by this Activity</div>')
        '''
    return script


#TODO: multiple Entity SPARQL
def get_activity_generated_entities_svg(activity_uri):
    script = ''
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT *
        WHERE { GRAPH ?g {
          { <''' + activity_uri + '''> prov:generated ?u . }
          UNION
          { ?u prov:wasGeneratedBy <''' + activity_uri + '''> .}
          OPTIONAL {?u rdf:label ?t .}
        } }
    '''

    activity_results = functions_db.db_query_secure(query)
    if activity_results and 'results' in activity_results:
        #gen = json.loads(activity_results[1])['results']
        gen = activity_results['results']
        if len(gen['bindings']) > 0:
            if gen['bindings'][0].get('t'):
                title = gen['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(gen['bindings'][0]['u']['value'])

            script += '''
                //Entity (used)                title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity/?uri=''' + uri_encoded + '''">' +
                            '         ''' + title + '''' +
                            '     </a>' +
                            '</div>';
                var entityGenTitle = svgContainer.append('foreignObject')
                                .attr('x', 525)
                                .attr('y', 250)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
                var entityGen = svgContainer.append("ellipse")
                                        .attr("cx", 599)
                                        .attr("cy", 250)
                                        .attr("rx", 100)
                                        .attr("ry", 64)
                                        .attr("fill", "#ffffbe")
                                        .attr("stroke", "grey")
                                        .attr("stroke-width", "1");

                //Entity class name
                var entityGenName = svgContainer.append("text")
                                        .attr("x", 599)
                                        .attr("y", 230)
                                        .text("Entity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Entity (used) arrow
                var entityGenArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "425,249, 489,249, 489,244, 499,250, 489,257, 489,251, 425,251");

                //Entity (used) arrow name
                var entityGenArrowName = svgContainer.append("text")
                                        .attr("x", 480)
                                        .attr("y", 190)
                                        .text("prov:generated")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Entity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity/?uri=''' + uri_encoded + '''">' +
                            '         ''' + title + '''' +
                            '     </a>' +
                            '</div>';
                var entityGenTitle = svgContainer.append('foreignObject')
                                .attr('x', 525)
                                .attr('y', 250)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
            if len(gen['bindings']) > 1:
                if gen['bindings'][1].get('t'):
                    title = gen['bindings'][1]['t']['value']
                else:
                    title = 'uri'
                uri_encoded = urllib.quote(gen['bindings'][1]['u']['value'])

                script += '''
                    //Entity (used)
                    var entityGen = svgContainer.append("ellipse")
                                            .attr("cx", 599)
                                            .attr("cy", 100)
                                            .attr("rx", 100)
                                            .attr("ry", 64)
                                            .attr("fill", "#ffffbe")
                                            .attr("stroke", "grey")
                                            .attr("stroke-width", "1");

                    //Entity class name
                    var entityGenName = svgContainer.append("text")
                                            .attr("x", 599)
                                            .attr("y", 80)
                                            .text("Entity")
                                            .style("font-family", "Verdana")
                                            .style("text-anchor", "middle");

                    //Entity (used) arrow
                    var entityGenArrow = svgContainer.append("polygon")
                                            .style("stroke-width", "1")
                                            .attr("points", "425,249, 520,150, 524,153, 524,142, 514,144, 518,148, 425,247");

                    //Entity title
                    title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                                '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity/?uri=''' + uri_encoded + '''">' +
                                '         ''' + title + '''' +
                                '     </a>' +
                                '</div>';
                    var entityGenTitle = svgContainer.append('foreignObject')
                                    .attr('x', 525)
                                    .attr('y', 100)
                                    .attr('width', 147)
                                    .attr('height', 60)
                                    .append("xhtml:body")
                                    .html(title_html);
                '''
                if len(gen['bindings']) == 3:
                    if gen['bindings'][2].get('t'):
                        title = gen['bindings'][2]['t']['value']
                    else:
                        title = 'uri'
                    uri_encoded = urllib.quote(gen['bindings'][2]['u']['value'])

                    script += '''
                        //Entity (used)
                        var entityGen = svgContainer.append("ellipse")
                                                .attr("cx", 599)
                                                .attr("cy", 400)
                                                .attr("rx", 100)
                                                .attr("ry", 64)
                                                .attr("fill", "#ffffbe")
                                                .attr("stroke", "grey")
                                                .attr("stroke-width", "1");

                        //Entity class name
                        var entityGenName = svgContainer.append("text")
                                                .attr("x", 599)
                                                .attr("y", 380)
                                                .text("Entity")
                                                .style("font-family", "Verdana")
                                                .style("text-anchor", "middle");

                        //Entity (used) arrow
                        var entityGenArrow = svgContainer.append("polygon")
                                                .style("stroke-width", "1")
                                                .attr("points", "425,251, 520,350, 524,347, 524,358, 514,356, 518,352, 425,253");

                        //Entity title
                        title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                                    '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity/?uri=''' + uri_encoded + '''">' +
                                    '         ''' + title + '''' +
                                    '     </a>' +
                                    '</div>';
                        var entityGenTitle = svgContainer.append('foreignObject')
                                        .attr('x', 525)
                                        .attr('y', 400)
                                        .attr('width', 147)
                                        .attr('height', 60)
                                        .append("xhtml:body")
                                        .html(title_html);
                    '''
                elif len(gen['bindings']) > 3:
                    # < 3
                    script = ''  # reset script
                    script += '''
                        //Entity (used)
                        var entityGen1 = svgContainer.append("ellipse")
                                                .attr("cx", 599)
                                                .attr("cy", 250)
                                                .attr("rx", 100)
                                                .attr("ry", 64)
                                                .attr("fill", "#ffffbe")
                                                .attr("stroke", "grey")
                                                .attr("stroke-width", "1");

                        var entityGen2 = svgContainer.append("ellipse")
                                                .attr("cx", 594)
                                                .attr("cy", 255)
                                                .attr("rx", 100)
                                                .attr("ry", 64)
                                                .attr("fill", "#ffffbe")
                                                .attr("stroke", "grey")
                                                .attr("stroke-width", "1");

                        var entityGenN = svgContainer.append("ellipse")
                                                .attr("cx", 589)
                                                .attr("cy", 260)
                                                .attr("rx", 100)
                                                .attr("ry", 64)
                                                .attr("fill", "#ffffbe")
                                                .attr("stroke", "grey")
                                                .attr("stroke-width", "1");

                        //Entity class name
                        var entityGenName = svgContainer.append("text")
                                                .attr("x", 589)
                                                .attr("y", 240)
                                                .text("Entity")
                                                .style("font-family", "Verdana")
                                                .style("text-anchor", "middle");

                        //Entity (used) arrow
                        var uentityGenArrow = svgContainer.append("polygon")
                                                .style("stroke-width", "1")
                                                .attr("points", "425,249, 479,249, 479,244, 489,250, 479,257, 479,251, 425,251");

                        //Entity (used) arrow name
                        var uentityGenArrowName = svgContainer.append("text")
                                                .attr("x", 480)
                                                .attr("y", 190)
                                                .text("prov:generated")
                                                .style("font-family", "Verdana")
                                                .style("font-size", "smaller")
                                                .style("text-anchor", "middle");

                        //Entity title
                        title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                                    '   Multiple Entities, click ' +
                                    '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''function/sparql/">here</a> ' +
                                    '   to search' +
                                    '</div>';
                        var entityGenTitle = svgContainer.append('foreignObject')
                                        .attr('x', 525)
                                        .attr('y', 250)
                                        .attr('width', 147)
                                        .attr('height', 60)
                                        .append("xhtml:body")
                                        .html(title_html);
                    '''
        else:
            # zero
            pass
    else:
        #we have a fault
        script += '''
            var entityGenFaultText = svgContainer.append('foreignObject')
                                    .attr('x', 349)
                                    .attr('y', 200)
                                    .attr('width', 149)
                                    .attr('height', 100)
                                    .append("xhtml:body")
                                    .html('<div style="width: 149px;">There is a fault with retrieving Entities that may have been used by this Activity</div>')
        '''
    return script


#TODO: multiple Activity SPARQL
def get_activity_was_informed_by(activity_uri):
    script = ''
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT *
        WHERE { GRAPH ?g {
            <''' + activity_uri + '''> a prov:Activity .
            <''' + activity_uri + '''> prov:wasInformedBy ?wif .
            OPTIONAL { ?wif rdf:label ?t . }
        } }
    '''
    activity_results = functions_db.db_query_secure(query)

    if activity_results and 'results' in activity_results:
        #wif = json.loads(activity_results[1])['results']
        wif = activity_results['results']
        if len(wif['bindings']) == 1:
            if wif['bindings'][0].get('t'):
                title = wif['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wif['bindings'][0]['wif']['value'])
            script += '''
                //Activity (wasDerivedFrom)
                var activityWIB = svgContainer.append("rect")
                                        .attr("x", 275)
                                        .attr("y", 399)
                                        .attr("width", 150)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                //Activity class name
                var activityWIBName = svgContainer.append("text")
                                        .attr("x", 350)
                                        .attr("y", 420)
                                        .text("Activity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Activity (wasInformedBy) arrow
                var activityWIBArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "349,301, 349,388, 344,388, 350,398, 356,388, 351,388, 351,301");

                //Activity (wasInformedBy) arrow name
                var activityWIBArrowName = svgContainer.append("text")
                                        .attr("x", 350)
                                        .attr("y", 350)
                                        .text("prov:wasInformedBy")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Activity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#cfceff;">' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/activity/?uri=''' + uri_encoded + '''">' +
                            '         ''' + title + '''' +
                            '     </a>' +
                            '</div>';
                var activityTitle = svgContainer.append('foreignObject')
                                .attr('x', 276)
                                .attr('y', 435)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        elif len(wif['bindings']) > 1:
            script += '''
                //Activity (wasDerivedFrom)
                var activityWIB = svgContainer.append("rect")
                                        .attr("x", 275)
                                        .attr("y", 399)
                                        .attr("width", 150)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                var activityWIB = svgContainer.append("rect")
                                        .attr("x", 270)
                                        .attr("y", 394)
                                        .attr("width", 150)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                var activityWIB = svgContainer.append("rect")
                                        .attr("x", 265)
                                        .attr("y", 389)
                                        .attr("width", 150)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                //Activity class name
                var activityWIBName = svgContainer.append("text")
                                        .attr("x", 350)
                                        .attr("y", 420)
                                        .text("Activity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Activity (wasInformedBy) arrow
                var activityWIBArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "349,301, 349,378, 344,378, 350,388, 356,378, 351,378, 351,301");

                //Activity (wasInformedBy) arrow name
                var activityWIBArrowName = svgContainer.append("text")
                                        .attr("x", 350)
                                        .attr("y", 350)
                                        .text("prov:wasInformedBy")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Activity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#cfceff;">' +
                            '   Multiple Activities, click ' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''function/sparql/">here</a> ' +
                            '   to search' +
                            '</div>';
                var activityTitle = svgContainer.append('foreignObject')
                                .attr('x', 266)
                                .attr('y', 435)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        else:
            #do nothing as no Activities found
            pass
    else:
        #we have a fault
        script += '''
            var activityUsedFaultText = svgContainer.append('foreignObject')
                                    .attr('x', 550)
                                    .attr('y', 200)
                                    .attr('width', 149)
                                    .attr('height', 100)
                                    .append("xhtml:body")
                                    .html('<div style="width: 149px;">There is a fault with retrieving Activities that may have used this Entity</div>')
        '''

    return script


#
#   Agents
#
def get_agents_dict():
    query = '''
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT DISTINCT ?ag ?n
        WHERE { GRAPH ?g {
            {
                { ?e a prov:Entity . }
                UNION
                { ?e a prov:Plan . }
                ?e prov:wasAttributedTo ?ag .
                OPTIONAL{ ?ag foaf:name ?n . }
            }
            UNION
            {
                ?a a prov:Activity .
                ?a prov:wasAssociatedWith ?ag .
                OPTIONAL{ ?ag foaf:name ?n . }
            }
            UNION
            {
                ?ag1 a prov:Agent .
                ?ag1 prov:actedOnBehalfOf ?ag .
                OPTIONAL{ ?ag foaf:name ?n . }
            }
        } }
        '''
    agents = functions_db.db_query_secure(query)
    agent_items = []
    if agents and 'results' in agents:
        for agent in agents['results']['bindings']:
            ret = {}
            ret['ag'] = urllib.quote(str(agent['ag']['value']))
            ret['ag_u'] = str(agent['ag']['value'])
            if agent.get('n'):
                ret['n'] = str(agent['n']['value'])
            agent_items.append(ret)
    return agent_items


def get_agent(agent_uri):
    query = '''
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT DISTINCT (<''' + agent_uri + '''> AS ?ag) ?n ?ag2
        WHERE { GRAPH ?g {
            {
                { ?e a prov:Entity . }
                UNION
                { ?e a prov:Plan . }
                OPTIONAL{ ?e prov:wasAttributedTo <''' + agent_uri + '''> . }
                OPTIONAL{ <''' + agent_uri + '''> foaf:name ?n . }
                OPTIONAL{ <''' + agent_uri + '''> prov:actedOnBehalfOf ?ag2 . }
            }
            UNION
            {
                ?e a prov:Activity .
                OPTIONAL{ ?e prov:wasAssociatedWith <''' + agent_uri + '''> . }
                OPTIONAL{ <''' + agent_uri + '''> foaf:name ?n . }
                OPTIONAL{ <''' + agent_uri + '''> prov:actedOnBehalfOf ?ag2 . }
            }
            UNION
            {
                ?aoo a prov:Agent .
                ?aoo prov:actedOnBehalfOf <''' + agent_uri + '''> .
                OPTIONAL{ <''' + agent_uri + '''> foaf:name ?n . }
            }
            UNION
            {
                <''' + agent_uri + '''> a prov:Agent .
                OPTIONAL{ <''' + agent_uri + '''> foaf:name ?n . }
                OPTIONAL{ <''' + agent_uri + '''> prov:actedOnBehalfOf ?ag2 . }
            }
        } }
        '''
    return functions_db.db_query_secure(query)


def get_agent_dict(agent_uri):
    agent_detail = get_agent(agent_uri)
    ret = {}
    if agent_detail and 'results' in agent_detail and len(agent_detail['results']['bindings']) > 0:
        if 'n' in agent_detail['results']['bindings'][0]:
            ret['n'] = agent_detail['results']['bindings'][0]['n']['value']
        else:
            ret['n'] = agent_uri
        ret['uri'] = agent_uri
    return ret


def get_agent_details_svg(agent_uri):
    get_agent_result = get_agent(agent_uri)
    #check for any faults
    if get_agent_result[0]:
        agent_details = json.loads(get_agent_result[1])
        #check we got a result
        if len(agent_details['results']['bindings']) > 0:
            script = '''
                var svgContainer = d3.select("#container-content-2").append("svg")
                                                    .attr("width", 700)
                                                    .attr("height", 500);

                //Agent
                var agent = svgContainer.append("polygon")
                                        .style("stroke", "black")
                                        .style("fill", "moccasin")
                                        .style("stroke-width", "1")
                                        .attr("points", "350,200, 435,225, 435,300, 265,300, 265,225");

                //Agent class name
                var agentName = svgContainer.append("text")
                                        .attr("x", 350)
                                        .attr("y", 240)
                                        .text("Agent")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");
            '''
            #print its name, if it has one
            if agent_details['results']['bindings'][0].get('n'):
                name = agent_details['results']['bindings'][0]['n']['value']
            else:
                name = agent_details['results']['bindings'][0]['ag']['value']
                name = name.split('#')
                if len(name) < 2:
                    name = agent_uri.split('/')
                name = name[-1]
            script += '''
                //Activity title
                var agentName = svgContainer.append('foreignObject')
                                        .attr('x', 275)
                                        .attr('y', 260)
                                        .attr('width', 148)
                                        .attr('height', 100)
                                        .append("xhtml:body")
                                        .html('<div style="width: 149px; font-size:smaller; background-color:moccasin;">''' + name + '''</div>')
            '''

            #print actedOnBehalfOf, if it has one
            if agent_details['results']['bindings'][0].get('ag2'):
                agent_uri = agent_details['results']['bindings'][0]['ag2']['value']
                agent_uri_encoded = urllib.quote(agent_uri)
                agent_name = agent_details['results']['bindings'][0]['ag2']['value']
                agent_name = agent_name.split('#')
                if len(agent_name) < 2:
                    agent_name = agent_uri.split('/')
                agent_name = agent_name[-1]
                script += '''
                    //Agent
                    var agent = svgContainer.append("polygon")
                                            .style("stroke", "black")
                                            .style("fill", "moccasin")
                                            .style("stroke-width", "1")
                                            .attr("points", "350,1, 435,25, 435,100, 265,100, 265,25");

                    //Agent class name
                    var agentName = svgContainer.append("text")
                                            .attr("x", 350)
                                            .attr("y", 40)
                                            .text("Agent")
                                            .style("font-family", "Verdana")
                                            .style("text-anchor", "middle");

                    //Agent (actedOnBehalfOf) arrow
                    var agentArrow = svgContainer.append("polygon")
                                            .style("stroke-width", "1")
                                            .attr("points", "349,201, 349,110, 344,110, 350,100, 356,110, 351,110, 351,201");

                    //Agent (wasAttributedTo) arrow name
                    var agentArrowName = svgContainer.append("text")
                                            .attr("x", 350)
                                            .attr("y", 150)
                                            .text("prov:actedOnBehalfOf")
                                            .style("font-family", "Verdana")
                                            .style("font-size", "smaller")
                                            .style("text-anchor", "middle");

                    //Agent name
                    var agentName = svgContainer.append('foreignObject')
                                            .attr('x', 275)
                                            .attr('y', 60)
                                            .attr('width', 148)
                                            .attr('height', 100)
                                            .append("xhtml:body")
                                            .html('<div style="width: 149px; font-size:smaller; background-color:moccasin; overflow:hidden;"><a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/agent/?uri=''' + agent_uri_encoded + '''">''' + agent_name + '''</a></div>')
                '''

            return [True, script]
        else:
            return [False, 'Not found']
    else:
        return [False, 'There was a fault']


#TODO: multiple Entity SPARQL
def get_agent_was_attributed_to_svg(agent_uri):
    script = ''
    query = '''
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT DISTINCT ?e ?t
        WHERE { GRAPH ?g {
            { ?e a prov:Entity .}
            UNION
            { ?e a prov:Plan .}
            ?e prov:wasAttributedTo <''' + agent_uri + '''> ;
            OPTIONAL { ?e rdf:label ?t . }
        } }
    '''
    entity_results = functions_db.db_query_secure(query)

    if entity_results[0]:
        wat = json.loads(entity_results[1])['results']
        if len(wat['bindings']) == 1:
            if wat['bindings'][0].get('t'):
                title = wat['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wat['bindings'][0]['e']['value'])
            script += '''
                //Entity (wasAttributedTo)
                var entityWDF = svgContainer.append("ellipse")
                                        .attr("cx", 350)
                                        .attr("cy", 435)
                                        .attr("rx", 100)
                                        .attr("ry", 64)
                                        .attr("fill", "#ffffbe")
                                        .attr("stroke", "grey")
                                        .attr("stroke-width", "1");

                //Entity class name
                var entityWATName = svgContainer.append("text")
                                        .attr("x", 350)
                                        .attr("y", 420)
                                        .text("Entity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Entity (wasAttributedTo) arrow
                var entityWATArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "349,370, 349,311, 344,311, 350,301, 356,311, 351,311, 351,370");

                //Entity (wasAttributedTo) arrow name
                var entityWATArrowName = svgContainer.append("text")
                                        .attr("x", 350)
                                        .attr("y", 350)
                                        .text("prov:wasAttributedTo")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Activity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity/?uri=''' + uri_encoded + '''">' +
                            '         ''' + title + '''' +
                            '     </a>' +
                            '</div>';
                var entityTitle = svgContainer.append('foreignObject')
                                .attr('x', 275)
                                .attr('y', 435)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        elif len(wat['bindings']) > 1:
            script += '''
                //Activity (used) multiple
                var entityWAT1 = svgContainer.append("ellipse")
                                        .attr("cx", 350)
                                        .attr("cy", 435)
                                        .attr("rx", 100)
                                        .attr("ry", 64)
                                        .attr("fill", "#ffffbe")
                                        .attr("stroke", "grey")
                                        .attr("stroke-width", "1");

                var entityWAT2 = svgContainer.append("ellipse")
                                        .attr("cx", 345)
                                        .attr("cy", 430)
                                        .attr("rx", 100)
                                        .attr("ry", 64)
                                        .attr("fill", "#ffffbe")
                                        .attr("stroke", "grey")
                                        .attr("stroke-width", "1");

                var entityWATN = svgContainer.append("ellipse")
                                        .attr("cx", 340)
                                        .attr("cy", 425)
                                        .attr("rx", 100)
                                        .attr("ry", 64)
                                        .attr("fill", "#ffffbe")
                                        .attr("stroke", "grey")
                                        .attr("stroke-width", "1");

                //Entit(y|ies) class name
                var entityWATName = svgContainer.append("text")
                                        .attr("x", 340)
                                        .attr("y", 400)
                                        .text("Entity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Entity (wasAttributedTo) arrow
                var entityWATArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "349,360, 349,311, 344,311, 350,301, 356,311, 351,311, 351,360");

                //Entity (wasAttributedTo) arrow name
                var entityWATArrowName = svgContainer.append("text")
                                        .attr("x", 350)
                                        .attr("y", 340)
                                        .text("prov:wasAttributedTo")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Entity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#ffffbe;">' +
                            '   Multiple Entities, click ' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''function/sparql/">here</a> ' +
                            '   to search' +
                            '</div>';
                var entityTitle = svgContainer.append('foreignObject')
                                .attr('x', 275)
                                .attr('y', 425)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        else:
            #do nothing as no Activities found
            pass
    else:
        #we have a fault
        script += '''
            var activityUsedFaultText = svgContainer.append('foreignObject')
                                    .attr('x', 550)
                                    .attr('y', 200)
                                    .attr('width', 149)
                                    .attr('height', 100)
                                    .append("xhtml:body")
                                    .html('<div style="width: 149px;">There is a fault with retrieving Activities that may have used this Entity</div>')
        '''

    return script


#TODO: multiple Activity SPARQL
def get_agent_was_associated_with_svg(agent_uri):
    script = ''
    query = '''
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT DISTINCT ?a ?t
        WHERE { GRAPH ?g {
            { ?a a prov:Activity .}
            ?a prov:wasAssociatedWith <''' + agent_uri + '''> ;
            OPTIONAL { ?a rdf:label ?t . }
        } }
    '''
    activity_results = functions_db.db_query_secure(query)

    if activity_results[0]:
        waw = json.loads(activity_results[1])['results']
        if len(waw['bindings']) == 1:
            if waw['bindings'][0].get('t'):
                title = waw['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(waw['bindings'][0]['a']['value'])
            script += '''
                //Activity (wasGeneratedBy)
                var activityWGB = svgContainer.append("rect")
                                        .attr("x", 1)
                                        .attr("y", 200)
                                        .attr("width", 150)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                //Activity class name
                var activityWGBName = svgContainer.append("text")
                                        .attr("x", 75)
                                        .attr("y", 230)
                                        .text("Activity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Activity (wasGeneratedBy) arrow
                var activityWGBArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "150,249, 255,249, 255,244, 265,250, 255,257, 255,251, 150,251");

                //Activity (wasGeneratedBy) arrow name
                var activityUsedArrowName = svgContainer.append("text")
                                        .attr("x", 200)
                                        .attr("y", 195)
                                        .text("prov:wasAssociatedWith")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Activity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#cfceff;">' +
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/activity/?uri=''' + uri_encoded + '''">' +
                            '         ''' + title + '''' +
                            '     </a>' +
                            '</div>';
                var activityTitle = svgContainer.append('foreignObject')
                                .attr('x', 2)
                                .attr('y', 240)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        elif len(waw['bindings']) > 1:
            script += '''
                //Activity (wasGeneratedBy)
                var activityWGB1 = svgContainer.append("rect")
                                        .attr("x", 1)
                                        .attr("y", 200)
                                        .attr("width", 150)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                var activityWGB2 = svgContainer.append("rect")
                                        .attr("x", 6)
                                        .attr("y", 205)
                                        .attr("width", 150)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                var activityWGBN = svgContainer.append("rect")
                                        .attr("x", 11)
                                        .attr("y", 210)
                                        .attr("width", 150)
                                        .attr("height", 100)
                                        .attr("fill", "#cfceff")
                                        .attr("stroke", "blue")
                                        .attr("stroke-width", "1");

                //Activity class name
                var activityWGBName = svgContainer.append("text")
                                        .attr("x", 85)
                                        .attr("y", 240)
                                        .text("Activity")
                                        .style("font-family", "Verdana")
                                        .style("text-anchor", "middle");

                //Activity (wasGeneratedBy) arrow
                var activityWGBArrow = svgContainer.append("polygon")
                                        .style("stroke-width", "1")
                                        .attr("points", "160,249, 255,249, 255,244, 265,250, 255,257, 255,251, 160,251");

                //Activity (wasGeneratedBy) arrow name
                var activityUsedArrowName = svgContainer.append("text")
                                        .attr("x", 200)
                                        .attr("y", 195)
                                        .text("prov:wasAssociatedWith")
                                        .style("font-family", "Verdana")
                                        .style("font-size", "smaller")
                                        .style("text-anchor", "middle");

                //Activity title
                title_html = '<div style="width: 147px; font-size:smaller; background-color:#cfceff;">' +
                            '         Multiple Activities, click <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''function/sparql">here</a> to search'+
                            '</div>';
                var activityTitle = svgContainer.append('foreignObject')
                                .attr('x', 12)
                                .attr('y', 250)
                                .attr('width', 147)
                                .attr('height', 60)
                                .append("xhtml:body")
                                .html(title_html);
            '''
        else:
            #do nothing as no Activities found
            pass
    else:
        #we have a fault
        script += '''
            var activityUsedFaultText = svgContainer.append('foreignObject')
                                    .attr('x', 1)
                                    .attr('y', 200)
                                    .attr('width', 149)
                                    .attr('height', 100)
                                    .append("xhtml:body")
                                    .html('<div style="width: 149px;">There is a fault with retrieving Activities that may be associated with this Agent</div>')
        '''

    return script


#
#   Pages
#


#TODO: add create Agent with details option
#TODO: add links to Basic & External docco


def create_report_formparts(form_parts_json_obj):
    #agent-new-existing [new, existing]
    #   - agent (URI)
    #   - agent-name, agent-URI, agent-email

    #report-type [BasicReport, ExternalReport]
    #report-title
    #report-reportingsystem (URI-encoded)
    #report-nativeId

    #activity-title
    #activity-description
    #activity-startedAtTime
    #activity-endedAtTime

    pass


def page_register_reporting_system():
    html = '''
    <h1>Provenance Management Service</h1>
    <h2>Register a <em>Reporting System</em></h2>
    <h3 style="color:red; font-style:italic;">Coming!</h3>
    '''
    return html


def replace_placeholder_uuids(original_turtle):
    new_turtle = original_turtle
    base_uri = settings.PROMS_INSTANCE_NAMESPACE_URI
    if base_uri.endswith('/'):
        base_uri = base_uri[:-1]
    while 1:
        pat = '<%s([^>]*)#([^>]*)>' % ('http://placeholder.org')
        x = re.compile(pat)
        m = re.search(x, new_turtle)
        if not m:
            break
        new_uri = '<' + base_uri + m.group(1) + "#" + str(uuid.uuid4()) + '>'
        original_uri = '<http://placeholder.org' + m.group(1) + '#' + m.group(2) + '>'
        new_turtle = new_turtle.replace(original_uri, new_uri)
    return new_turtle