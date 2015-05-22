import functions_db
import settings
import cStringIO
from rdflib import Graph
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

            svg_script = get_reportingsystem_details_svg(ret)
            if svg_script[0] == True:
                rs_script = svg_script[1]
                rs_script += get_reportingsystem_reports_svg(reportingsystem_uri)
                ret['rs_script'] = rs_script
    return ret


def get_reports_for_rs_query(reportingsystem_uri):
    query = '''
PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX proms: <http://promsns.org/def/proms#>
SELECT  *
WHERE {
    GRAPH ?g {
        { ?r a proms:Report }
        UNION
        { ?r a proms:BasicReport }
        UNION
        { ?r a proms:ExternalReport }
        UNION
        { ?r a proms:InternalReport }
        ?r proms:reportingSystem <''' + reportingsystem_uri + '''> .
        ?r rdf:label ?t .
        ?r proms:nativeId ?job .
        ?r proms:endingActivity ?sat .
        ?sat prov:endedAtTime ?eat .
    }
}
ORDER BY DESC(?eat)
    '''
    return query

#TODO: get ordering by Report --> Activity --> startedAtTime
def get_reports_for_rs(reportingsystem_uri):
    query = get_reports_for_rs_query(reportingsystem_uri)
    return functions_db.db_query_secure(query)


def get_reportingsystem_details_svg(reportingsystem_dict):
    rLabel = reportingsystem_dict.get('t', 'Untitled')
    script = '''
        var rLabel = "''' + rLabel + '''";
        var reportingSystem = addReportingSystem(35, 5, rLabel, "", "");
    '''
    return [True, script]


def get_reportingsystem_reports_svg(reportingsystem_uri):
    #add in all the Reports for this ReportingSystem
    reports = get_reports_for_rs(reportingsystem_uri)
    if reports and reports['results']['bindings']:
        if len(reports['results']['bindings']) > 0:
            r1uri_encoded = urllib.quote(reports['results']['bindings'][0]['r']['value'])
            r1title = reports['results']['bindings'][0]['t']['value']
            r1jobId = reports['results']['bindings'][0]['job']['value']
            y_top = 5
            x_pos = 350
            reports_script = '''
                var reports = [];
                var report0 = addReport(''' + str(x_pos) + ''', ''' + str(y_top) + ''', "''' + r1title + '''", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/report/?uri=" + r1uri_encoded + '''", "''' + r1jobId + '''");
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
                        query = get_reports_for_rs_query(reportingsystem_uri)
                        query_encoded = urllib.quote(query)
                        reports_script += '''
                            var report = addReport(''' + str(x_pos) + ''', ''' + str(y_offset) + ''', "Multiple Reports, click to search", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "function/sparql/?query=" + query_encoded + '''");
                            reports.push(report);
                        '''
                        break
                    uri = report['r']['value']
                    uri_encoded = urllib.quote(uri);
                    title = report['t']['value']
                    jobId = report['job']['value']
                    reports_script += '''
                        var report = addReport(''' + str(x_pos) + ''', ''' + str(y_offset) + ''', "''' + title + '''", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/report/?uri=" + uri_encoded + '''", "''' + jobId + '''");
                        reports.push(report);
                    '''
                    i += 1
            reports_script += '''
                addConnectedLinks(reportingSystem, reports, "proms:reportingSystem");
            '''
        else:
            #no reports
            reports_script = ''
    else:
        #we have a fault
        reports_script = '''
            var reportUsedFaultText = addReport(550, 200, "There is a fault with retrieving Reports that may have used this ReportingSystem", "");
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
        WHERE {
            GRAPH ?g {
                { ?r a proms:BasicReport . }
                UNION
                { ?r a proms:ExternalReport . }
                UNION
                { ?r a proms:InternalReport . }
                ?r rdf:label ?t
            }
        }
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
        WHERE {
            GRAPH ?g {
                <''' + report_uri + '''> a ?rt .
                <''' + report_uri + '''> rdf:label ?l .
                <''' + report_uri + '''> proms:nativeId ?id .
                OPTIONAL { <''' + report_uri + '''> proms:reportingSystem ?rs } .
                OPTIONAL { <''' + report_uri + '''> proms:startingActivity ?sac .
                    ?sac prov:startedAtTime ?sat .
                    ?sac rdf:label ?sac_t
                } .
                OPTIONAL { <''' + report_uri + '''> proms:endingActivity ?eac .
                    ?eac prov:endedAtTime ?eat .
                    ?eac rdf:label ?eac_t .
                } .
            }
            OPTIONAL { ?rs rdf:label ?rs_t }
        }
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
            if('sac' in report_detail['results']['bindings'][0]):
                ret['sac'] = report_detail['results']['bindings'][index]['sac']['value']
                if('sat' in report_detail['results']['bindings'][0]):
                    ret['sat'] = report_detail['results']['bindings'][index]['sat']['value']
                if('sac_t' in report_detail['results']['bindings'][0]):
                    ret['sac_t'] = report_detail['results']['bindings'][index]['sac_t']['value']
            if('eac' in report_detail['results']['bindings'][0]):
                ret['eac'] = report_detail['results']['bindings'][index]['eac']['value']
                if('eat' in report_detail['results']['bindings'][0]):
                    ret['eat'] = report_detail['results']['bindings'][index]['eat']['value']
                if('eac_t' in report_detail['results']['bindings'][0]):
                    ret['eac_t'] = report_detail['results']['bindings'][index]['eac_t']['value']
            ret['uri'] = report_uri
            svg_script = get_report_details_svg(ret)
            if svg_script[0] == True:
                ret['r_script'] = svg_script[1]
    return ret


#TODO: Check if this is used
def get_report_metadata(report_uri):
    #TODO: landing page
    #get the report metadata from DB
    query = '''
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?rt ?t ?id ?rs ?rs_t ?sat
        WHERE {
            GRAPH ?g {
                <''' + report_uri + '''> a ?rt .
                <''' + report_uri + '''> rdf:label ?t .
                <''' + report_uri + '''> proms:nativeId ?id .
                <''' + report_uri + '''> proms:reportingSystem ?rs .
                ?rs rdf:label ?rs_t .
                <''' + report_uri + '''> proms:startingActivity ?sac .
                ?sac prov:startedAtTime ?sat .
            }
        }
    '''
    return functions_db.db_query_secure(query)


#TODO: draw Neighbours view for Report
def get_report_details_svg(report_dict):
    rLabel = report_dict.get('l', 'uri')
    script = '''
        var rLabel = "''' + rLabel + '''";
        var report = addReport(350, 200, rLabel, "");
    '''
    if report_dict.get('rs'):
        rsLabel = report_dict.get('rs_t', 'uri')
        rsUri = report_dict.get('rs', '')
        if rsUri != '':
            rsUri = settings.PROMS_INSTANCE_NAMESPACE_URI + "id/reportingsystem/?uri=" + rsUri
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
            var sacUri = "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/activity/?uri=" + sac_uri_encoded + '''";
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
                var eacUri = "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/activity/?uri=" + eac_uri_encoded + '''";
                var eacLabel = "''' + eac_label + '''";
                var sacActivity = addActivity(50, 120, sacLabel, sacUri);
                addLink(report, sacActivity, "proms:startingActivity", TOP);
                var eacActivity = addActivity(50, 280, eacLabel, eacUri);
                addLink(report, eacActivity, "proms:endingActivity", BOTTOM);
            '''
    return [True, script]


# XXX Unused
def get_report_activity_wgb_svg(entity_uri):
    script = ''
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?a ?t
        WHERE {
            GRAPH ?g {
                ?a prov:generated <''' + entity_uri + '''> .
                ?a rdf:label ?t .
            }
        }
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
            return [False, result[1]]
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
        WHERE {
            GRAPH ?g {
                { ?e rdf:label ?l . }
                { ?e a prov:Entity . }
                UNION
                { ?e a prov:Plan . }
                OPTIONAL { ?s rdf:label ?t . }
            }
        }
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
        WHERE {
            GRAPH ?g {
                OPTIONAL { <''' + entity_uri + '''> rdf:label ?l . }
                OPTIONAL { <''' + entity_uri + '''> dc:created ?c . }
                OPTIONAL { <''' + entity_uri + '''> dcat:downloadURL ?dl . }
                OPTIONAL {
                    { <''' + entity_uri + '''> a prov:Entity . }
                    UNION
                    { <''' + entity_uri + '''> a prov:Plan . }
                }
                OPTIONAL { <''' + entity_uri + '''> rdf:label ?t . }
                OPTIONAL { <''' + entity_uri + '''> prov:value ?v . }
                OPTIONAL { <''' + entity_uri + '''> prov:wasAttributedTo ?wat . }
                OPTIONAL { ?wat foaf:name ?wat_name . }
            }
        }
    '''
    return functions_db.db_query_secure(query)


def get_entity_dict(entity_uri):
    entity_detail = get_entity(entity_uri)
    ret = {}
    if entity_detail and 'results' in entity_detail:
        if len(entity_detail['results']['bindings']) > 0:
            ret['uri'] = entity_uri
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
            svg_script = get_entity_details_svg(ret)
            if svg_script[0] == True:
                e_script = svg_script[1]
                e_script += get_entity_activity_wgb_svg(entity_uri)
                e_script += get_entity_activity_used_svg(entity_uri)
                e_script += get_entity_entity_wdf_svg(entity_uri)
                ret['e_script'] = e_script

    return ret

def get_entity_details_svg(entity_dict):
    # Draw Entity
    eLabel = entity_dict.get('l', 'uri')
    script = '''
            var eLabel = "''' + eLabel + '''";
            var entity = addEntity(380, 255, eLabel, "");
    '''

    # Draw value if it has one
    if(entity_dict.get('v')):
        script += '''
            var value = addValue(305, 400, "''' + entity_dict.get('v') + '''");
            addLink(entity, value, "prov:value", RIGHT);
        '''

    # Draw Agent (if one exists)
    if entity_dict.get('wat'):
        agent_uri = entity_dict.get('wat')
        agent_uri_encoded = urllib.quote(agent_uri)
        agent_name = entity_dict.get('wat_name', '')
        if agent_name == '':
            agent_name = agent_uri.split('#')
            if len(agent_name) < 2:
                agent_name = agent_uri.split('/')
            agent_name = agent_name[-1]
            script += '''
                var agentLabel = "''' + agent_name + '''";
                var agentUri = "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/agent/?uri=" + agent_uri_encoded + '''";
                var agent = addAgent(305, 5, agentLabel, agentUri);
                addLink(entity, agent, "prov:wasAttributedTo", RIGHT);
            '''
    return [True, script]

def get_entity_activity_wgb_svg(entity_uri):
    script = ''
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?a ?t
        WHERE {
            GRAPH ?g {
                ?a prov:generated <''' + entity_uri + '''> .
                ?a rdf:label ?t .
            }
        }
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
                var aLabel = "''' + title + '''";
                var aUri = "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/activity/?uri=" + uri_encoded + '''";
                var activityWGB = addActivity(5, 205, aLabel, aUri);
                addLink(entity, activityWGB, "prov:wasGeneratedBy", TOP);
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
WHERE {
    GRAPH ?g {
        ?a prov:used <''' + entity_uri + '''> .
        ?a rdf:label ?t .
    }
}
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
            script = '''
                var aLabel = "''' + title + '''";
                var aUri = "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/activity/?uri=" + uri_encoded + '''";
                var activityUsed = addActivity(555, 205, aLabel, aUri);
                addLink(activityUsed, entity, "prov:used", TOP);
            '''
        # TODO: Test, no current Entities have multiple prov:used Activities
        elif len(used) > 1:
            # TODO: Check query
            query_encoded = urllib.quote(query)
            script += '''
                activityUsed1 = addActivity(555, 215, "", "");
                activityUsed2 = addActivity(550, 210, "", "");
                activityUsedN = addActivity(545, 205, "Multiple Activities, click to search", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "function/sparql/?query=" + query_encoded + '''");
                addLink(activityUsedN, entity, "prov:used", TOP);
            '''
        else:
            #do nothing as no Activities found
            pass
    else:
        #we have a fault
        script += '''
            var activityFault = addActivity(550, 205, "There is a fault with retrieving Activities that may have used this Entity", "");
        '''
    return script


#TODO: Untested
def get_entity_entity_wdf_svg(entity_uri):
    # XXX Could add the extra WDF to the original Entity query and not have to
    # re-query
    script = ''
    query = '''
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?e ?t
WHERE {
    GRAPH ?g {
        { <''' + entity_uri + '''> a prov:Entity . }
        UNION
        { <''' + entity_uri + '''> a prov:Plan . }
        <''' + entity_uri + '''> prov:wasDerivedFrom ?e .
        ?e rdf:label ?t .
    }
}
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
                var entityWDF = addEntity(355, 440, "''' + title + '''", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "/id/entity/?uri=" + uri_encoded + '''");
                drawLink(entityWDF, entity, "prov:wasDerivedFrom", TOP);
            '''
        elif len(wdf) > 1:
            #TODO: Check query
            query_encoded = urllib.quote(query)
            script += '''
                var entityWDF1 = addEntity(355, 440, "", "");
                var entityWDF2 = addEntity(350, 435, "", "");
                var entityWDFN = addEntity(345, 430, "Multiple Entities, click here to search", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "function/sparql/?query=" + query_encoded + '''");
                drawLink(entityWDFN, entity, "prov:wasDerivedFrom", TOP);
            '''
        else:
            #do nothing as no Activities found
            pass
    else:
        #we have a fault
        script += '''
            var entityFaultText = addEntity(350, 440, "There is a fault with retrieving Activities that may have used this Entity", "");
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
        WHERE {
            GRAPH ?g {
                ?a a prov:Activity .
                ?a rdf:label ?l
            }
        }
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
        WHERE {
            GRAPH ?g {
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
            }
        }
    '''
    return functions_db.db_query_secure(query)


def get_activity_dict(activity_uri):
    activity_detail = get_activity(activity_uri)
    ret = {}
    if activity_detail and 'results' in activity_detail:
        if len(activity_detail['results']['bindings']) > 0:
            ret['uri'] = activity_uri
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
            svg_script = get_activity_details_svg(ret)
            if svg_script[0] == True:
                a_script = svg_script[1]
                a_script += get_activity_used_entities_svg(activity_uri)
                a_script += get_activity_generated_entities_svg(activity_uri)
                a_script += get_activity_was_informed_by(activity_uri)
                ret['a_script'] = a_script
    return ret


def get_activity_details_svg(activity_dict):
    aLabel = activity_dict.get('l', 'uri')
    aUri = activity_dict.get('uri', '')
    script = '''
            var aLabel = "''' + aLabel + '''";
            var activity = addActivity(275, 200, aLabel, "");
    '''
    # print its Agent, if it has one
    if activity_dict.get('waw'):
        agent_uri = activity_dict.get('waw', '')
        agent_uri_encoded = urllib.quote(agent_uri)
        if activity_dict.get('waw_name'):
            agent_name = activity_dict.get('waw_name')
        else:
            agent_name = agent_uri.split('#')
            if len(agent_name) < 2:
                agent_name = agent_uri.split('/')
            agent_name = agent_name[-1]
        script += '''
            var agentName = "''' + agent_name + '''";
            var agentUri = "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/agent/?uri=" + agent_uri_encoded + '''";
            var agent = addAgent(275, 5, agentName, agentUri);
            addLink(activity, agent, "prov:wasAssociatedWith", RIGHT);
        '''
    return [True, script]


def get_activity_used_entities_svg(activity_uri):
    script = ''
    query = '''
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
SELECT *
WHERE {
    GRAPH ?g {
        <''' + activity_uri + '''> prov:used ?u .
        OPTIONAL {?u rdf:label ?t .}
    }
}
    '''
    activity_results = functions_db.db_query_secure(query)
    if activity_results and 'results' in activity_results:
        used = activity_results['results']
        if len(used['bindings']) > 0:
            if used['bindings'][0].get('t'):
                title = used['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(used['bindings'][0]['u']['value'])
            script += '''
                var entityUsed1 = addEntity(105, 250, "''' + title + '''", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/entity/?uri=" + uri_encoded + '''");
                addLink(activity, entityUsed1, "prov:used", TOP);
            '''
            # TODO: Loop this if 1-3 Entities
            if len(used['bindings']) > 1:
                if used['bindings'][1].get('t'):
                    title = used['bindings'][1]['t']['value']
                else:
                    title = 'uri'
                uri_encoded = urllib.quote(used['bindings'][1]['u']['value'])

                script += '''
                    var entityUsed2 = addEntity(105, 100, "''' + title + '''", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/entity/?uri=" + uri_encoded + '''");
                    addLink(activity, entityUsed2, "prov:used", TOP);
                '''
                if len(used['bindings']) == 3:
                    if used['bindings'][2].get('t'):
                        title = used['bindings'][2]['t']['value']
                    else:
                        title = 'uri'
                    uri_encoded = urllib.quote(used['bindings'][2]['u']['value'])

                    script += '''
                        var entityUsed3 = addEntity(105, 400, "''' + title + '''", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/entity/?uri=" + uri_encoded + '''");
                        addLink(activity, entityUsed3, "prov:used", RIGHT);
                    '''
                elif len(used['bindings']) > 3:
                    query_encoded = urllib.quote(query)
                    script = ''  # reset script
                    script += '''
                        var entityUsed1 = addEntity(105, 260, "", "");
                        var entityUsed2 = addEntity(100, 255, "", "");
                        var entityUsedN = addEntity(95, 250, "Multiple Entities, click here to search", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "function/sparql/?query=" + query_encoded + '''");
                        addLink(activity, entityUsedN, "prov:used", TOP);
                    '''
        else:
            # zero
            pass
    else:
        #we have a fault
        script += '''
            var entityUsedFaultText = addEntity(1, 200, "There is a fault with retrieving Entities that may have been used by this Activity", "");
        '''
    return script


def get_activity_generated_entities_svg(activity_uri):
    script = ''
    query = '''
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
SELECT *
WHERE {
    GRAPH ?g {
        { <''' + activity_uri + '''> prov:generated ?u . }
        UNION
        { ?u prov:wasGeneratedBy <''' + activity_uri + '''> .}
        OPTIONAL {?u rdf:label ?t .}
    }
}
    '''

    activity_results = functions_db.db_query_secure(query)
    if activity_results and 'results' in activity_results:
        gen = activity_results['results']
        if len(gen['bindings']) > 0:
            if gen['bindings'][0].get('t'):
                title = gen['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(gen['bindings'][0]['u']['value'])
            script += '''
                var entityGen1 = addEntity(605, 250, "''' + title + '''", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/entity/?uri=" + uri_encoded + '''");
                addLink(activity, entityGen1, "prov:generated", TOP);
            '''
            # Could make a loop to 3
            if len(gen['bindings']) > 1:
                if gen['bindings'][1].get('t'):
                    title = gen['bindings'][1]['t']['value']
                else:
                    title = 'uri'
                uri_encoded = urllib.quote(gen['bindings'][1]['u']['value'])

                script += '''
                    var entityGen2 = addEntity(605, 100, "''' + title + '''", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/entity/?uri=" + uri_encoded + '''");
                    addLink(activity, entityGen2, "prov:generated", TOP);
                '''
                if len(gen['bindings']) == 3:
                    if gen['bindings'][2].get('t'):
                        title = gen['bindings'][2]['t']['value']
                    else:
                        title = 'uri'
                    uri_encoded = urllib.quote(gen['bindings'][2]['u']['value'])

                    script += '''
                        var entityGen3 = addEntity(605, 400, "''' + title + '''", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/entity/?uri=" + uri_encoded + '''");
                        addLink(activity, entityGen3, "prov:generated", TOP);
                    '''
                elif len(gen['bindings']) > 3:
                    # TODO: Check query
                    query_encoded = urllib.quote(query)
                    script = ''  # reset script
                    script += '''
                        var entityGen1 = addEntity(615, 260, "", "");
                        var entityGen2 = addEntity(610, 255, "", "");
                        var entityGenN = addEntity(605, 250, "Multiple Entities, click here to search", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "function/sparql/?query=" + query_encoded + '''");
                        addLink(activity, entityGenN, "prov:generated", TOP);
                    '''
        else:
            # zero
            pass
    else:
        #we have a fault
        script += '''
            var entityGenFaultText = addEntity(349, 200, "There is a fault with retrieving Entities that may have been used by this Activity", "");
        '''
    return script


# TODO: Untested
def get_activity_was_informed_by(activity_uri):
    script = ''
    query = '''
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
SELECT *
WHERE {
    GRAPH ?g {
        <''' + activity_uri + '''> a prov:Activity .
        <''' + activity_uri + '''> prov:wasInformedBy ?wif .
        OPTIONAL { ?wif rdf:label ?t . }
    }
}
    '''
    activity_results = functions_db.db_query_secure(query)

    if activity_results and 'results' in activity_results:
        wif = activity_results['results']
        if len(wif['bindings']) == 1:
            if wif['bindings'][0].get('t'):
                title = wif['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wif['bindings'][0]['wif']['value'])
            script += '''
                var activityWIB = addActivity(275, 399, "''' + title + '''", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/activity/?uri=" + uri_encoded + '''");
                addLink(activity, activityWIB, "prov:wasInformedBy", RIGHT);
            '''
        # TODO: Check query
        elif len(wif['bindings']) > 1:
            query_encoded = urllib.quote(query)
            script += '''
                var activityWIB1 = addActivity(275, 399, "", "");
                var activityWIB2 = addActivity(270, 394, "", "")
                var activityWIBN = addActivity(2650, 389, "Multiple Activities, click here to search", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "function/sparql/?query=" + query_encoded + '''");
                addLink(activity, activityWIBN, "prov:wasInformedBy", RIGHT);
            '''
        else:
            #do nothing as no Activities found
            pass
    else:
        #we have a fault
        script += '''
            var activityUsedFaultText = addActivity(550, 200, "There is a fault with retrieving Activities that may have used this Entity", "");
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
        WHERE {
            GRAPH ?g {
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
            }
        }
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
        WHERE {
            GRAPH ?g {
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
            }
        }
        '''
    return functions_db.db_query_secure(query)


def get_agent_dict(agent_uri):
    agent_detail = get_agent(agent_uri)
    ret = {}
    if agent_detail and 'results' in agent_detail and len(agent_detail['results']['bindings']) > 0:
        ret['uri'] = agent_uri
        if 'n' in agent_detail['results']['bindings'][0]:
            ret['n'] = agent_detail['results']['bindings'][0]['n']['value']
        else:
            ret['n'] = agent_uri
        if 'ag2' in agent_detail['results']['bindings'][0]:
            ret['ag2'] = agent_detail['results']['bindings'][0]['ag2']['value']
        # TODO: Re-enable when it's more than just the Agent being displayed
        svg_script = get_agent_details_svg(ret)
        if svg_script[0] == True:
            a_script = svg_script[1]
            a_script += get_agent_was_attributed_to_svg(agent_uri)
            a_script += get_agent_was_associated_with_svg(agent_uri)
            ret['a_script'] = a_script
    return ret


def get_agent_details_svg(agent_dict):
    a_uri = agent_dict.get('uri');
    if agent_dict.get('n'):
        a_label = agent_dict.get('n')
    else:
        aLabel = a_uri
        aLabel = aLabel.split('#')
        if len(aLabel) < 2:
            aLabel = a_uri.split('/')
        name = aLabel[-1]
    script = '''
        var aLabel = "''' + a_label + '''";
        var agent = addAgent(310, 200, aLabel, "");
    '''

    #print actedOnBehalfOf, if it has one
    if agent_dict.get('ag2'):
        agent_uri = agent_dict.get('ag2')
        agent_uri_encoded = urllib.quote(agent_uri)
        agent_name = agent_uri
        agent_name = agent_name.split('#')
        if len(agent_name) < 2:
            agent_name = agent_uri.split('/')
        agent_name = agent_name[-1]
        script += '''
            var agentAOBO = addAgent(310, 5, "''' + agent_name + '''", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "id/agent/?uri=" + agent_uri_encoded + '''");
            addLink(agent, agentWOBO, "prov:actedOnBehalfOf", RIGHT);
        '''
    return [True, script]


def get_agent_was_attributed_to_svg(agent_uri):
    script = ''
    query = '''
PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT DISTINCT ?e ?t
WHERE {
    GRAPH ?g {
        { ?e a prov:Entity .}
        UNION
        { ?e a prov:Plan .}
        ?e prov:wasAttributedTo <''' + agent_uri + '''> ;
        OPTIONAL { ?e rdf:label ?t . }
    }
}
    '''
    entity_results = functions_db.db_query_secure(query)

    if entity_results and 'results' in entity_results:
        wat = entity_results['results']
        if len(wat['bindings']) == 1:
            if wat['bindings'][0].get('t'):
                title = wat['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wat['bindings'][0]['e']['value'])
            script += '''
                entityLabel = "''' + title + '''";
                entityUri = "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity/?uri=''' + uri_encoded + '''";
                var entityWAT = addEntity(385, 430, entityLabel, entityUri);
                addLink(entity, entityWAT, "prov:wasAttributedTo", RIGHT);
            '''
        elif len(wat['bindings']) > 1:
            # TODO: Check query
            query_encoded = urllib.quote(query)
            script += '''
                var entityWAT1 = addEntity(395, 440, "", "");
                var entityWAT2 = addEntity(390, 435, "", "");
                var entityWATN = addEntity(385, 430, "Multiple Entities, click here to search", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "function/sparql/?query=" + query_encoded + '''");
                addLink(agent, entityWATN, "prov:wasAttributedTo", RIGHT);
            '''
        else:
            #do nothing as no Activities found
            pass
    else:
        #we have a fault
        script += '''
            var addEntity(550, 200, "There is a fault with retrieving Activities that may have used this Entity", "");
        '''
    return script


def get_agent_was_associated_with_svg(agent_uri):
    script = ''
    query = '''
PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT DISTINCT ?a ?t
WHERE {
    GRAPH ?g {
        { ?a a prov:Activity . }
        ?a prov:wasAssociatedWith <''' + agent_uri + '''> ;
        OPTIONAL { ?a rdf:label ?t . }
    }
}
    '''
    activity_results = functions_db.db_query_secure(query)

    if activity_results and 'results' in activity_results:
        waw = activity_results['results']
        if len(waw['bindings']) == 1:
            if waw['bindings'][0].get('t'):
                title = waw['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(waw['bindings'][0]['a']['value'])
            script += '''
                activityLabel = "''' + title + '''";
                activityUri = "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/activity/?uri=''' + uri_encoded + '''";
                var activityWAW = addActivity(5, 200, activityLabel, activityUri);
                addLink(agent, activityWAW, "prov:wasAssociatedWith", TOP);
            '''
        elif len(waw['bindings']) > 1:
            # TODO: Check query
            query_encoded = urllib.quote(query)
            script += '''
                var activityWAW1 = addActivity(15, 210, "", "");
                var activityWAW2 = addActivity(10, 205, "", "");
                var activityWAWN = addActivity(5, 200, "Multiple Activities, click here to search", "''' + settings.PROMS_INSTANCE_NAMESPACE_URI + "function/sparql/?query=" + query_encoded + '''");
                addLink(agent, activityWAWN, "prov:wasAssociatedWith", TOP);
            '''
        else:
            #do nothing as no Activities found
            pass
    else:
        #we have a fault
        script += '''
            var activityUsedFaultText = addActivity(5, 200, "There is a fault with retrieving Activities that may be associated with this Agent", "");
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
