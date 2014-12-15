import settings
import re
import json
import pyproms
import cStringIO
from rdflib import Graph
import requests
from rulesets import proms
import urllib


def get_proms_html_header():
    html = requests.get('http://scikey.org/theme/template-header.inc').text

    nav = open(settings.HOME_DIR + settings.STATIC_DIR + 'nav.html', 'r').read()
    html = html.replace('<?php include $nav ?>', nav)
    html = re.sub(r'<title>(.*)</title>', '<title>PROMS: Provenance Management System</title>', html)
    style = '''
        <style>
            .lined {
                border: solid 2px black;
                border-collapse: collapse;

                font-family: Verdana;
                font-size: 12px;
            }
            .lined th,
            .lined td {
                border: solid 1px black;
                padding: 3px;
            }
            h4 {
                font-weight:bold;
            }

            .layout {
                border-collapse: collapse;
                border: none;
            }

            .layout th,
            .layout td {
                border: none;
            }
        </style>
    </head>
    '''
    html = re.sub('</head>', style, html)

    return html


def get_proms_html_footer():
    html = requests.get('http://scikey.org/theme/template-footer.inc').text
    html = html.replace('This web page is maintained', 'This system\'s web page is maintained')

    return html


def submit_stardog_query(query):
    uri = settings.PROMS_DB_URI
    qsa = {'query': query}
    h = {'accept': 'application/sparql-results+json'}
    r = requests.get(uri, params=qsa, headers=h, auth=('proms', 'proms'))

    if r.status_code == 200:
        return [True, r.text]
    else:
        return [False, 'ERROR: ' + r.text]


#
#   ReportingSystems
#
def get_reportingsystems():
    ''''''
    '''
    @prefix vcard:  <http://www.w3.org/2006/vcard/ns#> .
    @prefix :       <http://placeholder.org#> .

    :
        a proms:reportingSystem ;
        dc:title "Example Reporting System"^^xsd:string ;
        proms:owner [
            a vcard:Individual;
            vcard:fn "Nicholas Car";
            vcard:hasEmail <mailto:nicholas.car@csiro.au> ;
            vcard:hasAddress [ a vcard:Work;
                vcard:country-name "Australia";
                vcard:locality "Brisbane";
                vcard:postal-code "4152";
                vcard:street-address "EcoSciences Precinct, 41 Boggo Rd, Dutton Park" ];
            vcard:hasTelephone [ a vcard:Work,
                vcard:Voice;
                vcard:hasValue <tel:+61738335600> ];
        ]
    .
    '''
    query = '''
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX proms: <http://promsns.org/ns/proms#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        SELECT ?rs ?t ?fn ?em ?ph ?add
        WHERE {
          ?rs a proms:ReportingSystem .
          ?rs dc:title ?t .
          ?rs proms:owner ?o .
          ?o vcard:fn ?fn .
          ?o vcard:hasEmail ?em .
          ?o vcard:hasTelephone ?ph_1 .
          ?ph_1 vcard:hasValue ?ph .
          ?o vcard:hasAddress ?add_1 .
          ?add_1 vcard:locality ?add
        }
    '''

    return submit_stardog_query(query)


def get_reportingsystems_html(sparql_query_results_json):
    reportingsystms = json.loads(sparql_query_results_json)
    l = '<ul>'
    for reportingsystem in reportingsystms['results']['bindings']:
        if reportingsystem.get('t'):
            uri_encoded = urllib.quote(str(reportingsystem['rs']['value']))
            l += '<li><a href="' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/reportingsystem?uri=' + uri_encoded + '">' + str(reportingsystem['t']['value']) + '</a> (' + str(reportingsystem['rs']['value']) + ')</li>'
        else:
            l += '<li><a href="' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/reportingsystem?uri=' + str(reportingsystem['rs']['value']) + '">' + str(reportingsystem['rs']['value']) + '</a></li>'
    l += '</ul>'

    return l


def get_reportingsystems_dropdown(sparql_query_results_json):
    reportingsystems = json.loads(sparql_query_results_json)
    l = '<select name="report-reportingsystem" id="report-reportingsystem">'
    l += '<option value="">Select...</option>'
    for reportingsystem in reportingsystems['results']['bindings']:
        if reportingsystem.get('t'):
            uri_encoded = urllib.quote(str(reportingsystem['rs']['value']))
            l += '<option value="' + uri_encoded + '">' + str(reportingsystem['t']['value']) + '</option>'
        else:
            l += '<option value="' + str(reportingsystem['rs']['value']) + '">' + str(reportingsystem['rs']['value']) + '</option>'
    l += '</select>'

    return l


def get_reportingsystem(reportingsystem_uri):
    query = '''
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX proms: <http://promsns.org/ns/proms#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        SELECT ?t ?fn ?em ?ph ?add
        WHERE {
          <''' + reportingsystem_uri + '''> a proms:ReportingSystem .
          <''' + reportingsystem_uri + '''> dc:title ?t .
          <''' + reportingsystem_uri + '''> proms:owner ?o .
          ?o vcard:fn ?fn .
          ?o vcard:hasEmail ?em .
          ?o vcard:hasTelephone ?ph_1 .
          ?ph_1 vcard:hasValue ?ph .
          ?o vcard:hasAddress ?add_1 .
          ?add_1 vcard:locality ?add
        }
    '''

    return submit_stardog_query(query)


def draw_report(n, uri, title, jobId):
    uri_encoded = urllib.quote(uri)
    y_offset = n * 130
    y1 = y_offset + 16
    y2 = y_offset + 16
    y3 = y_offset + 97
    y4 = y_offset + 117
    y5 = y_offset + 117
    y_label = y_offset + 40

    ya1 = y_offset + 49
    ya2 = y_offset + 49
    ya3 = y_offset + 44
    ya4 = y_offset + 50
    ya5 = y_offset + 57
    ya6 = y_offset + 51
    ya7 = y_offset + 51

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

        //Report N arrow
        var reportNArrow = svgContainer.append("polygon")
                                .style("stroke-width", "1")
                                .attr("points", "250,''' + str(ya1) + ''' 192,''' + str(ya1) + ''' 192,''' + str(ya1-130) + ''' 190,''' + str(ya1-130) + ''' 190,''' + str(ya6) + ''' 250,''' + str(ya6) + ''' ");

        //Report N title
        var entityTitle = svgContainer.append('foreignObject')
                                .attr('x', 250)
                                .attr('y', ''' + str(y_offset + 47) + ''')
                                .attr('width', 138)
                                .attr('height', 95)
                                .append("xhtml:body")
                                .html('<div style="width:138px; color:white; font-size:smaller; background-color:MediumVioletRed;"><a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/report/?uri=''' + uri_encoded + '''">''' + title + '''</a><br />jobId: ''' + jobId + '''</div>')
    '''

    return svg


def get_reportingsystem_reports_svg(reportingsystem_uri):
    #add in all the Reports for this ReportingSystem
    query = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX proms: <http://promsns.org/ns/proms#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    SELECT  *
    WHERE {
      {?r a proms:BasicReport}
      UNION
      {?r a proms:ExternalReport}
      UNION
      {?r a proms:InternalReport}
      ?r proms:reportingSystem <''' + reportingsystem_uri + '''> .
      ?r dc:title ?t .
      ?r proms:jobId ?job .
      ?r proms:endingActivity ?sat .
      ?sat prov:endedAtTime ?eat .
    }
    ORDER BY DESC(?eat)
    '''
    reports = submit_stardog_query(query)
    if reports[1]:
        rp = json.loads(reports[1])
        if len(rp['results']['bindings']) > 0:
            r1uri_encoded = urllib.quote(rp['results']['bindings'][0]['r']['value'])
            r1title = rp['results']['bindings'][0]['t']['value']
            r1jobId = rp['results']['bindings'][0]['job']['value']
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
                                    .html('<div style="width:138px; color:white; font-size:smaller; background-color:MediumVioletRed;"><a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/report/?uri=''' + r1uri_encoded + '''">''' + r1title + '''</a><br />jobId: ''' + r1jobId + '''</div>')

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

            if len(rp['results']['bindings']) > 1:
                reports = rp['results']['bindings'][1:]
                i = 1
                for report in reports:
                    uri = rp['results']['bindings'][i]['r']['value']
                    title = rp['results']['bindings'][i]['t']['value']
                    jobId = rp['results']['bindings'][i]['job']['value']
                    reports_script += draw_report(i, uri, title, jobId)
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


#TODO: complete get_reportingsystem_html()
#TODO: think about expanding SVG area with report count
def get_reportingsystem_html(reportingsystem_uri):
    reportingsystem_details = get_reportingsystem(reportingsystem_uri)
    if reportingsystem_details[0]:
        r = json.loads(reportingsystem_details[1])
        title = r['results']['bindings'][0]['t']['value']
        html = '''
            <table class="lined">
                <tr><th>Title:</th><td>''' + title + '''</td></tr>
                <tr><th>Owner:</th><td>''' + r['results']['bindings'][0]['fn']['value'] + '''</td></tr>
            </table>
        '''

        #get the list of reports
        reports_script = get_reportingsystem_reports_svg(reportingsystem_uri)

        html += '''
            <h4>Neighbours view</h4>
            <script src="/static/js/d3.min.js" charset="utf-8"></script>
            <style>
                svg {
                    /*border: solid 1px #eeeeee;*/
                    margin-left:75px;
                }
            </style>
            <script>
                var svgContainer = d3.select("#container-content-2").append("svg")
                                                    .attr("width", 700)
                                                    .attr("height", 500);

                //ReportingSystem
                var reportingSystem = svgContainer.append("polygon")
                                        .attr("stroke", "grey")
                                        .attr("stroke-width", "1")
                                        .attr("fill", "purple")
                                        .attr("points", "31,16 111,16 141,46 141,126 111,156 31,156 1,126 1,46");

                //ReportingSystem class name
                var reportingSystemGenName = svgContainer.append("text")
                                        .attr("x", 70)
                                        .attr("y", 66)
                                        .text("ReportingSystem")
                                        .style("font-family", "Verdana")
                                        .style("fill", "white")
                                        .style("text-anchor", "middle");

                //ReportingSystem title
                var entityTitle = svgContainer.append('foreignObject')
                                        .attr('x', 2)
                                        .attr('y', 81)
                                        .attr('width', 138)
                                        .attr('height', 95)
                                        .append("xhtml:body")
                                        .html('<div style="width:138px; color:white; font-size:smaller; background-color:purple;">''' + title + '''</div>')

                ''' + reports_script + '''
            </script>
        '''
    else:
        html = '''
            <h4>''' + reportingsystem_details[1] + '''</h4>
        '''

    return html


def put_reportingsystem(reportingsystem_in_turtle):
    #replace the document's placeholder URI with one generated by this PROMS instance
    import uuid
    doc_uri = settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/reportingsystem/' + str(uuid.uuid4())
    report_in_turtle = reportingsystem_in_turtle.replace('http://placeholder.org#', doc_uri)
    #try to make a graph of the input text
    g = Graph()
    try:
        g.parse(cStringIO.StringIO(report_in_turtle), format="n3")
    except Exception as e:
        return [False, ['Could not parse input: ' + str(e)]]

    #conformance
    from rulesets import reportingsystems
    conf_results = reportingsystems.ReportingSystems(g).get_result()
    if conf_results['rule_results'][0]['passed']:
        #passed conformance so sent to DB
        #put data into a SPARQL 1.1 INSERT DATA query
        insert_query = 'INSERT DATA {' + g.serialize(format='n3') + '}'

        #insert into Stardog using the HTTP API
        uri = 'http://localhost:5820/proms/update'
        h = {'content-type': 'application/sparql-update'}
        r = requests.post(uri, data=insert_query, headers=h, auth=('proms', 'proms'))

        if r.status_code == 200:
            return [True, doc_uri]
        else:
            return [False, r.text]
    else:
        return [False, conf_results['rule_results'][0]['fail_reasons']]


#
#   Reports
#
def get_reports():
    query = '''
                PREFIX dc: <http://purl.org/dc/elements/1.1/>
                SELECT DISTINCT ?r ?t
                WHERE {
                  { ?r a proms:BasicReport . }
                  UNION
                  { ?r a proms:ExternalReport . }
                  UNION
                  { ?r a proms:InternalReport . }
                  ?r dc:title ?t .
                }
                ORDER BY ?r
            '''
    return submit_stardog_query(query)


#TODO: get this query working
#TODO: get ordering by Rport --> Activity --> startedAtTime
def get_reports_for_rs(reportingsystem_uri):
    query = '''
                PREFIX proms: <http://promsns.org/ns/proms#>
                PREFIX dc: <http://purl.org/dc/elements/1.1/>
                SELECT ?r ?t
                WHERE {
                  { ?r a proms:BasicReport . }
                  UNION
                  { ?r a proms:ExternalReport . }
                  UNION
                  { ?r a proms:InternalReport . }
                  ?r dc:title ?t .
                  #?r proms:reportingSystem <''' + reportingsystem_uri + '''#> .
                }
                ORDER BY ?r
            '''
    return submit_stardog_query(query)


def get_report_metadata(report_uri):
    #TODO: landing page
    #get the report metadata from DB
    query = '''
        PREFIX proms: <http://promsns.org/ns/proms#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?rt ?t ?job ?rs ?rs_t ?sat
        WHERE {
          <''' + report_uri + '''> a ?rt .
          <''' + report_uri + '''> dc:title ?t .
          <''' + report_uri + '''> proms:jobId ?job .
          <''' + report_uri + '''> proms:reportingSystem ?rs .
          ?rs dc:title ?rs_t .
          <''' + report_uri + '''> proms:startingActivity ?sac .
          ?sac prov:startedAtTime ?sat .
        }
    '''
    return submit_stardog_query(query)


def get_reports_html(sparql_query_results_json):
    import urllib

    reports = json.loads(sparql_query_results_json)

    l = '<ul>'
    for report in reports['results']['bindings']:
        uri_encoded = urllib.quote(str(report['r']['value']))
        l += '<li><a href="/id/report?uri=' + uri_encoded + '">' + str(report['t']['value']) + '</a> (' + str(report['r']['value']) + ')</li>'
    l += '</ul>'

    return l


#TODO: draw Neighbours view for Report
def get_report_details_svg():
    pass


def get_report_html(report_uri):
    report_details = get_report_metadata(report_uri)
    if report_details[0]:
        r = json.loads(report_details[1])
        rt = r['results']['bindings'][0]['rt']['value']
        rs = r['results']['bindings'][0]['rs']['value']
        rs_t = r['results']['bindings'][0]['rs_t']['value']
        rs_encoded = urllib.quote(rs)
        if rt == 'http://promsns.org/ns/proms#InternalReport':
            html = '<h4><a class="definition" href="http://promsns.org/ns/proms#ExternalReport">Internal</a> Report</h4>'
            html += '<table class="lines">'
            html += '  <tr><th>Title:</th><td>' + r['results']['bindings'][0]['t']['value'] + '</td></tr>'
            html += '  <tr><th>Reporting System:</th><td><a href="' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/reportingsystem/?uri=' + rs_encoded + '">' + rs_t + '</td></tr>'
            html += '  <tr><th>JobId:</th><td>' + r['results']['bindings'][0]['job']['value'] + '</td></tr>'
            html += '</table>'
        elif rt == 'http://promsns.org/ns/proms#ExternalReport':
            html = '<h4><a class="definition" href="http://promsns.org/ns/proms#ExternalReport">External</a> Report</h4>'
            html += '<table class="lines">'
            html += '  <tr><th>Title:</th><td>' + r['results']['bindings'][0]['t']['value'] + '</td></tr>'
            html += '  <tr><th>Reporting System:</th><td><a href="' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/reportingsystem/?uri=' + rs_encoded + '">' + rs_t + '</td></tr>'
            html += '  <tr><th>JobId:</th><td>' + r['results']['bindings'][0]['job']['value'] + '</td></tr>'
            html += '</table>'
        else:
            #Basic
            html = '<h4><a class="definition" href="http://promsns.org/ns/proms#BasicReport">Basic</a> Report</h4>'
            html += '<table class="lines">'
            html += '  <tr><th>Title:</th><td>' + r['results']['bindings'][0]['t']['value'] + '</td></tr>'
            html += '  <tr><th>Reporting System:</th><td><a href="' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/reportingsystem/?uri=' + rs_encoded + '">' + rs_t + '</td></tr>'
            html += '  <tr><th>JobId:</th><td>' + r['results']['bindings'][0]['job']['value'] + '</td></tr>'
            html += '</table>'

            #Neighbours view
            #Report starting/ending Activity

    else:
        html = '''
            <h4>''' + report_details[1] + '''</h4>
        '''

    return html


#TODO: remove hash from URI rewrite
def put_report(report_in_turtle):
    #replace the document's placeholder URI with one generated by this PROMS instance
    import uuid
    doc_uri = settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/report/' + str(uuid.uuid4()) + '#'
    report_in_turtle = report_in_turtle.replace('http://placeholder.org#', doc_uri)
    #try to make a graph of the input text
    g = Graph()
    try:
        g.parse(cStringIO.StringIO(report_in_turtle), format="n3")
    except Exception as e:
        return [False, ['Could not parse input: ' + str(e)]]

    #conformance
    conf_results = proms.Proms(g).get_result()
    if conf_results['rule_results'][0]['passed']:
        #passed conformance so sent to DB
        #put data into a SPARQL 1.1 INSERT DATA query
        insert_query = 'INSERT DATA {' + g.serialize(format='n3') + '}'

        #insert into Stardog using the HTTP API
        uri = 'http://localhost:5820/proms/update'
        h = {'content-type': 'application/sparql-update'}
        r = requests.post(uri, data=insert_query, headers=h, auth=('proms', 'proms'))

        if r.status_code == 200:
            return [True]
        else:
            return [False, r.text]
    else:
        return [False, conf_results['rule_results'][0]['fail_reasons']]


#
#   Entities
#
def get_entities():
    query = '''
                PREFIX dc: <http://purl.org/dc/elements/1.1/>
                SELECT DISTINCT ?e ?t
                WHERE {
                  { ?e a prov:Entity . }
                  UNION
                  { ?e a prov:Plan . }
                  OPTIONAL { ?s dc:title ?t . }
                }
                ORDER BY ?e
            '''
    return submit_stardog_query(query)


def get_entity(entity_uri):
    #TODO: landing page with view options:
    #   wasDerivedFrom, wasGeneratedBy, inv. used, hadPrimarySource, wasAttributedTo, value
    #get the report metadata from DB
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT DISTINCT ?t ?v ?wat ?wat_name
        WHERE {
            { <''' + entity_uri + '''> a prov:Entity . }
            UNION
            { <''' + entity_uri + '''> a prov:Plan . }
            OPTIONAL { <''' + entity_uri + '''> dc:title ?t . }
            OPTIONAL { <''' + entity_uri + '''> prov:value ?v . }
            OPTIONAL { <''' + entity_uri + '''> prov:wasAttributedTo ?wat . }
            OPTIONAL { ?wat foaf:name ?wat_name . }
        }
    '''
    return submit_stardog_query(query)


def get_entities_html(sparql_query_results_json):
    entities = json.loads(sparql_query_results_json)
    l = '<ul>'
    for entity in entities['results']['bindings']:
        if entity.get('t'):
            uri_encoded = urllib.quote(str(entity['e']['value']))
            l += '<li><a href="' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/entity?uri=' + uri_encoded + '">' + str(entity['t']['value']) + '</a> (' + str(entity['e']['value']) + ')</li>'
        else:
            l += '<li><a href="' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/entity?uri=' + str(entity['e']['value']) + '">' + str(entity['e']['value']) + '</a></li>'
    l += '</ul>'

    return l


def get_entities_dropdown(sparql_query_results_json):
    agents = json.loads(sparql_query_results_json)
    l = '<option value="">Select...</option>'
    for agent in agents['results']['bindings']:
        if agent.get('t'):
            uri_encoded = urllib.quote(str(agent['e']['value']))
            l += '<option value="' + uri_encoded + '">' + str(agent['t']['value']) + '</option>'
        else:
            l += '<option value="' + str(agent['e']['value']) + '">' + str(agent['e']['value']) + '</option>'
    l += '</select>'

    return l


def get_entity_details_svg(entity_uri):
    get_entity_result = get_entity(entity_uri)
    #check for any faults
    if get_entity_result[0]:
        entity_details = json.loads(get_entity_result[1])
        #check we got a result
        if len(entity_details['results']['bindings']) > 0:
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
            if entity_details['results']['bindings'][0].get('t'):
                title = entity_details['results']['bindings'][0]['t']['value']
                script += '''
                    //Entity title
                    var entityTitle = svgContainer.append('foreignObject')
                                            .attr('x', 275)
                                            .attr('y', 250)
                                            .attr('width', 149)
                                            .attr('height', 100)
                                            .append("xhtml:body")
                                            .html('<div style="width: 149px; font-size:smaller; background-color:#ffffbe;">''' + title + '''</div>')
                '''
            #print its value, if it has one
            if entity_details['results']['bindings'][0].get('v'):
                value = entity_details['results']['bindings'][0]['v']['value']
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
                                            .html('<div style="width: 149px; font-size:smaller; background-color:white; overflow:hidden;">''' + value + '''</div>')

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
            if entity_details['results']['bindings'][0].get('wat'):
                agent_uri = entity_details['results']['bindings'][0]['wat']['value']
                agent_uri_encoded = urllib.quote(agent_uri)
                if entity_details['results']['bindings'][0].get('wat_name'):
                    agent_name = entity_details['results']['bindings'][0]['wat_name']['value']
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
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?a ?t
        WHERE {
          ?a prov:generated <''' + entity_uri + '''> .
          ?a dc:title ?t .
        }
    '''
    stardog_results = submit_stardog_query(query)

    if stardog_results[0]:
        wgb = json.loads(stardog_results[1])['results']
        if len(wgb['bindings']) == 1:
            if wgb['bindings'][0].get('t'):
                title = wgb['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wgb['bindings'][0]['a']['value'])

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
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?a ?t
        WHERE {
          ?a prov:used <''' + entity_uri + '''> .
          ?a dc:title ?t .
        }
    '''
    stardog_results = submit_stardog_query(query)

    if stardog_results[0]:
        used = json.loads(stardog_results[1])['results']
        if len(used['bindings']) == 1:
            if used['bindings'][0].get('t'):
                title = used['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(used['bindings'][0]['a']['value'])

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
        elif len(used['bindings']) > 1:
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
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''/function/sparql/">here</a> ' +
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
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT DISTINCT ?e ?t
        WHERE {
            { <''' + entity_uri + '''> a prov:Entity . }
            UNION
            { <''' + entity_uri + '''> a prov:Plan . }
            <''' + entity_uri + '''> prov:wasDerivedFrom ?e .
            ?e dc:title ?t .
        }
    '''
    stardog_results = submit_stardog_query(query)

    if stardog_results[0]:
        wdf = json.loads(stardog_results[1])['results']
        if len(wdf['bindings']) == 1:
            if wdf['bindings'][0].get('t'):
                title = wdf['bindings'][0]['t']['value']
            else:
                title = 'uri'
            uri_encoded = urllib.quote(wdf['bindings'][0]['e']['value'])
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
        elif len(wdf['bindings']) > 1:
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
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''/function/sparql/">here</a> ' +
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


def get_entity_html(entity_uri):
    entity_script = get_entity_details_svg(entity_uri)
    if entity_script[0]:
        #Entity (main)
        script = entity_script[1]

        #Activity wasGeneratedBy
        script += get_entity_activity_wgb_svg(entity_uri)

        #Activity used
        script += get_entity_activity_used_svg(entity_uri)

        #Entity(s) wasDerivedFrom
        script += get_entity_entity_wdf_svg(entity_uri)

        html = '''
            <h4>Neighbours view</h4>
            <script src="/static/js/d3.min.js" charset="utf-8"></script>
            <style>
                svg {
                    /*border: solid 1px #eeeeee;*/
                    margin-left:75px;
                }
            </style>
            <script>
                ''' + script + '''
            </script>
        '''
    else:
        html = '''
            <h4>''' + entity_script[1] + '''</h4>
        '''

    return html


#
#   Activities
#
def get_activities():
    query = '''
                PREFIX dc: <http://purl.org/dc/elements/1.1/>
                SELECT DISTINCT ?s ?t
                WHERE {
                  ?s a prov:Activity .
                  ?s dc:title ?t .
                }
                ORDER BY ?s
            '''
    return submit_stardog_query(query)


def get_activities_html(sparql_query_results_json):
    reports = json.loads(sparql_query_results_json)
    l = '<ul>'
    for report in reports['results']['bindings']:
        if report.get('t'):
            uri_encoded = urllib.quote(str(report['s']['value']))
            l += '<li><a href="' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/activity?uri=' + uri_encoded + '">' + str(report['t']['value']) + '</a> (' + str(report['s']['value']) + ')</li>'
        else:
            l += '<li><a href="' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/activity?uri=' + str(report['s']['value']) + '">' + str(report['s']['value']) + '</a></li>'
    l += '</ul>'

    return l


def get_activity(activity_uri):
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT *
        WHERE {
          <''' + activity_uri + '''> a prov:Activity .
          <''' + activity_uri + '''> dc:title ?t .
          <''' + activity_uri + '''> prov:startedAtTime ?sat .
          <''' + activity_uri + '''> prov:endedAtTime ?eat .
          <''' + activity_uri + '''> prov:wasAssociatedWith ?waw .
          OPTIONAL {?waw foaf:name ?waw_name .}
        }
    '''
    return submit_stardog_query(query)


def get_activity_details_svg(activity_uri):
    get_activity_result = get_activity(activity_uri)
    #check for any faults
    if get_activity_result[0]:
        activity_details = json.loads(get_activity_result[1])
        #check we got a result
        if len(activity_details['results']['bindings']) > 0:
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
            if activity_details['results']['bindings'][0].get('t'):
                title = activity_details['results']['bindings'][0]['t']['value']
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
            if activity_details['results']['bindings'][0].get('waw'):
                agent_uri = activity_details['results']['bindings'][0]['waw']['value']
                agent_uri_encoded = urllib.quote(agent_uri)
                if activity_details['results']['bindings'][0].get('waw_name'):
                    agent_name = activity_details['results']['bindings'][0]['waw_name']['value']
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
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT *
        WHERE {
          <''' + activity_uri + '''> prov:used ?u .
          OPTIONAL {?u dc:title ?t .}
        }
    '''
    stardog_results = submit_stardog_query(query)
    if stardog_results[0]:
        used = json.loads(stardog_results[1])['results']
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
                                    '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''/function/sparql/">here</a> ' +
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
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT *
        WHERE {
          { <''' + activity_uri + '''> prov:generated ?u . }
          UNION
          { ?u prov:wasGeneratedBy <''' + activity_uri + '''> .}
          OPTIONAL {?u dc:title ?t .}
        }
    '''

    stardog_results = submit_stardog_query(query)
    if stardog_results[0]:
        gen = json.loads(stardog_results[1])['results']
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
                                    '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''/function/sparql/">here</a> ' +
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
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT *
        WHERE {
            <''' + activity_uri + '''> a prov:Activity .
            <''' + activity_uri + '''> prov:wasInformedBy ?wif .
            OPTIONAL { ?wif dc:title ?t . }
        }
    '''
    stardog_results = submit_stardog_query(query)

    if stardog_results[0]:
        wif = json.loads(stardog_results[1])['results']
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
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''/function/sparql/">here</a> ' +
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


def get_activity_html(activity_uri):
    activity_script = get_activity_details_svg(activity_uri)
    if activity_script[0]:
        #Activity (main)
        script = activity_script[1]

        #Activity used
        script += get_activity_used_entities_svg(activity_uri)

        #Activity generated
        script += get_activity_generated_entities_svg(activity_uri)

        #Activity wasInformedBy
        script += get_activity_was_informed_by(activity_uri)

        html = '''
            <h4>Neighbours view</h4>
            <script src="/static/js/d3.min.js" charset="utf-8"></script>
            <style>
                svg {
                    /*border: solid 1px #eeeeee;*/
                    margin-left:75px;
                }
            </style>
            <script>
                ''' + script + '''
            </script>
        '''
    else:
        html = '''
            <h4>''' + activity_script[1] + '''</h4>
        '''

    return html


#
#   Agents
#
def get_agents():
    query = '''
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            SELECT DISTINCT ?ag ?n
            WHERE {
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
            '''
    return submit_stardog_query(query)


def get_agents_html(sparql_query_results_json):
    agents = json.loads(sparql_query_results_json)
    l = '<ul>'
    for agent in agents['results']['bindings']:
        if agent.get('n'):
            uri_encoded = urllib.quote(str(agent['ag']['value']))
            l += '<li><a href="' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/agent?uri=' + uri_encoded + '">' + str(agent['n']['value']) + '</a> (' + str(agent['ag']['value']) + ')</li>'
        else:
            l += '<li><a href="' + settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/agent?uri=' + str(agent['ag']['value']) + '">' + str(agent['ag']['value']) + '</a></li>'
    l += '</ul>'

    return l


def get_agents_dropdown(sparql_query_results_json):
    agents = json.loads(sparql_query_results_json)
    l = '<select name="agent" id="agent">'
    l += '<option value="">Select...</option>'
    for agent in agents['results']['bindings']:
        if agent.get('n'):
            uri_encoded = urllib.quote(str(agent['ag']['value']))
            l += '<option value="' + uri_encoded + '">' + str(agent['n']['value']) + '</option>'
        else:
            l += '<option value="' + str(agent['ag']['value']) + '">' + str(agent['ag']['value']) + '</option>'
    l += '</select>'

    return l


def get_agent(agent_uri):
    query = '''
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT DISTINCT (<''' + agent_uri + '''> AS ?ag) ?n ?ag2
            WHERE {
                {
                    { ?e a prov:Entity . }
                    UNION
                    { ?e a prov:Plan . }
                    ?e prov:wasAttributedTo <''' + agent_uri + '''> .
                    OPTIONAL{ <''' + agent_uri + '''> foaf:name ?n . }
                    OPTIONAL{ <''' + agent_uri + '''> prov:actedOnBehalfOf ?ag2 . }
                }
                UNION
                {
                    ?e a prov:Activity .
                    ?e prov:wasAssociatedWith <''' + agent_uri + '''> .
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
            '''
    return submit_stardog_query(query)


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
            PREFIX dc: <http://purl.org/dc/elements/1.1/>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT DISTINCT ?e ?t
            WHERE {
                { ?e a prov:Entity .}
                UNION
                { ?e a prov:Plan .}
                ?e prov:wasAttributedTo <''' + agent_uri + '''> ;
                OPTIONAL { ?e dc:title ?t . }
            }
    '''
    stardog_results = submit_stardog_query(query)

    if stardog_results[0]:
        wat = json.loads(stardog_results[1])['results']
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
                            '     <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''/function/sparql/">here</a> ' +
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
            PREFIX dc: <http://purl.org/dc/elements/1.1/>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT DISTINCT ?a ?t
            WHERE {
                { ?a a prov:Activity .}
                ?a prov:wasAssociatedWith <''' + agent_uri + '''> ;
                OPTIONAL { ?a dc:title ?t . }
            }
    '''
    stardog_results = submit_stardog_query(query)

    if stardog_results[0]:
        waw = json.loads(stardog_results[1])['results']
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


def get_agent_html(agent_uri):
    agent_script = get_agent_details_svg(agent_uri)
    if agent_script[0]:
        #Agent (main)
        script = agent_script[1]

        #Agent wasAttributedTo
        script += get_agent_was_attributed_to_svg(agent_uri)

        #Agent wasAssociatedWith
        script += get_agent_was_associated_with_svg(agent_uri)

        html = '''
            <h4>Neighbours view</h4>
            <script src="/static/js/d3.min.js" charset="utf-8"></script>
            <style>
                svg {
                    /*border: solid 1px #eeeeee;*/
                    margin-left:75px;
                }
            </style>
            <script>
                ''' + script + '''
            </script>
        '''
    else:
        html = '''
            <h4>''' + agent_script[1] + '''</h4>
        '''

    return html


#
#   Pages
#
def page_home():
    html = get_proms_html_header()
    html += '''
    <h1>Provenance Management System</h1>
    <p style="font-style: italic;">Under development, November, 2014.</p>
    <h4>This is the index page for the PROMS (PROvenance Management System) data store. It contains a database to store provenance data and a series of functions to manage that data.</h4>
    <h4>Getting Strated</h4>
    <p>Follow the links above to the right in the blue to navigate this system.</p>
    <h4>Documentation</h4>
    <p>Please visit the documentation page for details of service endpoints and features:</p>
    <ul>
        <li><a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''documentation">Documentation Page</a></li>
    </ul>
    <h4>Maintenance &amp; Contact</h4>
    <p>PROMS v3 is maintained by CSIRO's software engineers, led by Nicholas Car &amp; Matthew Stenson in CSIRO's Land &amp; Water Flagship, EcoScienes, Brisbane.</p>
    <p>Contact Nicholas with any issues:</p>
    <p>
        <strong>Nicholas Car</strong><br />
        <strong>ph:</strong> +61 7 3833 5600<br />
        <strong>e:</strong> <a href="mailto:nicholas.car@csiro.au">nicholas.car@csiro.au</a>
    </p>
    <h4>Licensing</h4>
    <p>PROMS v3 is licensed using the CSIRO Open Source Software License, based on the MIT/BSD Open Source License:</p>
    <ul>
        <li><a href="https://wiki.csiro.au/pages/viewpage.action?pageId=663847169">CSIRO Open Source Software License</a></li>
    </ul>
    <h4>Code</h4>
    <p>The code for PROV v3 is available from CSIRO's Stash code repository manager as the a Git repository:</p>
    <ul>
        <li><a href="https://stash.csiro.au/projects/EIS/repos/PROMS">PROMS v3 Git Repository</a></li>
    </ul>
    '''

    html += get_proms_html_footer()
    return html


def page_documentation():
    html = get_proms_html_header()
    html += '''
    <h1>Provenance Management Service</h1>
    <h2>Documentation for PROMS v3</h2>
    <p style="font-style: italic;">Under development, November, 2014.</p>
    <h3>Overview</h3>
    <p>PROMS v3 is a provenance storage system. It is an <a href="http://en.wikipedia.org/wiki/Application_programming_interface" class="definition">API</a> that wraps a graph database (see <a href="">database</a> below for more on this) used to store provenance traces.</p>
    <p>It does a few things to ensure that the data coming in from <em><a href="#" class="definition" style="text-decoration:line-through;">Reporting Systems</a></em> is acceptable and useful, it:</p>
    <ul>
        <li>validates incoming <a href="#" class="definition" style="text-decoration:line-through;">Reports</a> using the PROMS <a href="#" style="text-decoration:line-through;">Validation Criteria</a></li>
        <li>allows <a href="http://www.w3.org/standards/semanticweb/inference" class="definition">inference</a> to take place on <em>Reports</em></li>
        <li>provides <a href="http://en.wikipedia.org/wiki/Representational_state_transfer" class="definition">RESTful</a> endpoints to each of the classes of object that valid <em>Reports</em> contain</li>
    </ul>
    <h3>Data</h3>
    <p>PROMS v3 uses an extension to the <a href="http://www.w3.org/TR/prov-o/">PROV</a> <a class="definition" href="http://en.wikipedia.org/wiki/Ontology_%28information_science%29">ontology</a> (PROV-O) as its data model.</p>
    <p>Basic use of PROV-O includes the use of 3 basic classes of things:</p>
    <ul>
        <li><em>Entities</em> - things like datasets, files etc.</li>
        <li><em>Activities</em> - things that happen to make or use Entities</li>
        <li><em>Agents</em> - people or systems responsible for Activities (and thus Entities)</li>
    </ul>
    <p>PROMS extends the PROV-O into a <a href="http://promsns.org/def/proms">PROMS-O</a> by the inclusion of the following classes of thinfgs:</p>
    <ul>
        <li><em>Report</em> - a subclass of <em>Entity</em> with the following subclasses of its own:</li>
        <li><em>BasicReport</em> - a Report about an event (Activity) containing very basic metada: "something called X happened"</li>
        <li><em>ExternalReport</em> - a Report about an Activity with basic metadata and references to the input and output data it used</li>
        <li><em>InternalReport</em> - a Report with basic metadata and a full (as full as the author can make it) details about the internal steps of the Activity, modelled in PROV</li>
    </ul>
    <h3>Functions</h3>
    <p>The functions supported by PROMS v3 are:</p>
    <ul>
        <li>
            <strong>Create a new <em>Report</em></strong>
            <ul>
                <li>use the default <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''function/create_report"><em>Report</em> creation form</a></li>
                <li>HTTP POST a pre-made <em>Report</em> in the <a class="definition" href="http://www.w3.org/TeamSubmission/turtle/">RDF turtle</a> format to {PROMS_INSTANCE_URI}/id/report/</li>
            </ul>
        </li>
        <li>
            <strong>Create a pingback</strong> <em>(under development)</em>
            <ul>
                <li>let PROMS know you've referred to one of its <em>Entities</em> in a provenance graph elsewhere</li>
                <li>send a pingback JSON document to {PROMS_INSTANCE_URI}/function/pingback/</li>
            </ul>
        </li>
        <li>
            <strong>Browse <em>Reports</em> and their members</strong>
            <ul>
                <li>browse and filter <em>Reports</em> and their components <em>Entities</em> &amp; <em>Activities</em></li>
                <li><em>ReportingSystems</em> - <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/reportingsystem/">{PROMS_INSTANCE_URI}/id/reportingsystem/</a></li>
                <li><em>Reports</em> - <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/report/">{PROMS_INSTANCE_URI}/id/report/</a></li>
                <li><em>Entities</em> - <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/entity/">{PROMS_INSTANCE_URI}/id/entity/</a></li>
                <li><em>Activities</em> - <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/activity/">{PROMS_INSTANCE_URI}/id/activity/</a></li>
                <li><em>Agents</em> - <a href="''' + settings.PROMS_INSTANCE_NAMESPACE_URI + '''id/agent/">{PROMS_INSTANCE_URI}/id/agent/</a></li>
            </ul>
        </li>
        <li>
            <strong>Search the database</strong> <em>(under development)</em>
            <ul>
                <li>search the provenance data using PROM's SPARQL endpoint - <a href="/function/sparql">{PROMS_INSTANCE_URI}/function/sparql</a></li>
            </ul>
        </li>
    </ul>
    <h3 id="howto">How Tos</h3>
    <p><em>Coming, November, 2014!</em></p>
    <h3>Implementation</h3>
    <p>PROMS v3 is implemented according to Figure 1.</p>
    <div class="figure">
        <img src="/static/img/PROMS3_structure.png" alt="PROMS3 Structure" />
        <p class="caption"><strong>Figure 1</strong>: PROMS v3 Structure</p>
    </div>
    <h3 id="resources">Resources</h3>
    <p>Toolkits exist to generate PROMS <a class="definition" href="http://www.promsns.org/ns/proms#Report">Report</a>s that can then be lodged with this system.</p>
    <table class="lined">
        <tr><th>Toolkit</th><th>Technologies</th><th>Location</th></tr>
        <tr><td>PROMS Java client</td><td>Java, Jena (a Java RDF system)</td><td><a href="https://stash.csiro.au/projects/EIS/repos/proms-clients-java">https://stash.csiro.au/projects/EIS/repos/proms-clients-java</a></td></tr>
        <tr><td>pyproms<br />Python PROMS client module</td><td>Python (2.7), rdflib (a Python RDF framework)</td><td><a href="https://pypi.python.org/pypi/pyproms">pyproms on the Python package index</a></td></tr>
        <tr><td></td><td></td><td></td></tr>
        <tr><td></td><td></td><td></td></tr>
    </table>
    <h3>More details</h3>
    <p>Further documentation for PROMS and its related tools and concepts is maintained on the PROMS wiki:</p>
    <ul>
        <li><a href="https://wiki.csiro.au/display/PROMS/">https://wiki.csiro.au/display/PROMS/</a></li>
    </ul>
    '''

    html += get_proms_html_footer()

    return html


#TODO: add create Agent with details option
#TODO: add links to Basic & External docco
def page_create_report():

    html = get_proms_html_header()
    html += '''
    <h1>Provenance Management Service</h1>
    <h2>Create a <em>Report</em></h2>
    <p>This page allows someone toget_entities create a provenance <a class="definition" href="http://www.promsns.org/ns/proms#Report">Report</a> which can then be lodged with this instance of PROMS or downloaded for use elsewhere. Given that there are tools for creating complex <em>Reports</em> for a series of programming environments (see <a href="/documentation#resources">Documentation &gt; Resources</a>, this page is limited to creating simple <a class="definition" href="http://www.promsns.org/ns/proms#BasicReport">Basic</a> and <a class="definition" href="http://www.promsns.org/ns/proms#ExternalReport">External</a> <em>Reports</em>and cannot produce the more detailed <a class="definition" href="http://www.promsns.org/ns/proms#InternalReport">Internal</a> <em>Reports</em>.</p>
    <p>Complete the form below to create a <em>Report</em>. Input validation will ensure that the <em>Report</em> is valid.</p>
    <script src="/static/js/jquery.min.js" charset="utf-8"></script>
    <link rel="stylesheet" type="text/css" href="/static/css/jquery.datetimepicker.css"/ >
    <script src="/static/js/jquery.datetimepicker.js"></script>
    <style>
        .entity-input-delete,
        .entity-output-delete,
        .entity-input-add,
        .entity-output-add {
            color: #0f4a84;
            cursor: pointer;
            text-decoration: underline;
        }
    </style>
    <script>
        var entityInputCounter = 0;
        var entityOutputCounter = 0;
        $(function() {
            $('input[name=agent-new-existing]').change(function () {
                if ($('input[name=agent-new-existing]:checked', '#create-report').val() == "existing") {
                    $('#agent-existing-value').show();
                    $('#agent-new-value').hide();
                } else {
                    $('#agent-existing-value').hide();
                    $('#agent-new-value').show();
                }
            });

            //DateTime picker
            $('#activity-startedAtTime').datetimepicker({
              format:'Y-m-d H:i:s' + get_time_zone_offset(),
              inline:true,
              lang:'en'
            });
            $('#activity-endedAtTime').datetimepicker({
              format:'Y-m-d H:i:s' + get_time_zone_offset(),
              inline:true,
              lang:'en'
            });

            //Entity Inputs
            $('body').on('click', '.entity-input-delete', function (event) {
                //get this number
                number_str = this.id.substr(this.id.lastIndexOf('-')+1, this.id.lastIndexOf('-')+2);

                //delete the row
                $('#entity-input-row-' + number_str).remove();
            });

            $('body').on('click', '.entity-input-add', function (event) {
                //get the largest entity-input number
                //increment the number
                entityInputCounter = entityInputCounter + 1
                number_inc_str = pad(entityInputCounter + 1, 2);
                console.log(number_inc_str);
                $('#entity-input-row-add').before('<tr id="entity-input-row-' + number_inc_str + '">' +
                                                        '<td>' +
                                                        '    <input type="radio" class="entity-used-new-existing" name="entity-' + number_inc_str + '-new-existing" value="existing" checked="checked" /> Existing <strong>or</strong>' +
                                                        '    <input type="radio" class="entity-used-new-existing" name="entity-' + number_inc_str + '-new-existing" value="new" /> New' +
                                                        '</td>' +
                                                  '     <td><input type="text" class="entity-input" name="entity-input-' + number_inc_str + '" id="entity-input-' + number_inc_str + '" /></td>'+
                                                  '     <td><span class="entity-input-delete" id="entity-input-delete-' + number_inc_str + '">delete</span></td>'+
                                                  '</tr>');
            });

            $('body').on('change', 'input.entity-used-new-existing', function (event) {
                //TODO: complete new/existing Entity selection
                alert($(this).attr('name'));
            });

            $('#generate-report').click(function(event) {
                event.preventDefault();
                //validate fields


                //construct the JSON object from form fields
                var form_parts_json_obj = new Object();
                form_parts_json_obj.agent_new_existing = $('input[name=agent-new-existing]:checked', '#create-report').val();
                form_parts_json_obj.agent = $('#agent').val();
                form_parts_json_obj.agent_name = $('#agent-name').val();
                form_parts_json_obj.agent_uri = $('#agent-uri').val();
                form_parts_json_obj.agent_email = $('#agent-email').val();
                form_parts_json_obj.report_type = $('#report-type').val();
                form_parts_json_obj.report_title = $('#report-title').val();
                form_parts_json_obj.report_reportingsystem = $('#report-reportingsystem').val();
                form_parts_json_obj.report_nativeId = $('#report-nativeId').val();
                form_parts_json_obj.activity_title = $('#activity-title').val();
                form_parts_json_obj.activity_description = $('#activity-description').val();
                form_parts_json_obj.activity_startedAtTime = $('#activity-startedAtTime').val();
                form_parts_json_obj.activity_endedAtTime = $('#activity-endedAtTime').val();

                console.log(form_parts_json_obj);

                //post the JSON object to PROMS to convert it into Turtle
                /*
                $.ajax({
                    type: "POST",
                    url: url,
                    data: data,
                    success: success,
                    dataType: dataType
                });
                */

                //show the results to the user
                $('#generated-results').text("This is text");
                $('#generated-results').show();
            });
        });

        //only Australian timezones handles so far
        function get_time_zone_offset( ) {
            var current_date = new Date();
            switch (-current_date.getTimezoneOffset() / 60) {
                case 8:
                    ret = '+08:00';
                break;
                case 9:
                    ret = '+09:30';
                break;
                case 10:
                    ret = '+10:00';
                break;
                case 11:
                    ret = '+11:00';
                break;
            }
            return ret;
        }

        function pad(n, width, z) {
            z = z || '0';
            n = n + '';
            return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
        }
    </script>
    <form id="create-report" action="/function/create_report" method="post">
        <table class="lined" style="width:860px;">
            <tr><td colspan="2"><h3>Agent</h3></td></tr>
            <tr>
                <th style="width:300px;">
                    Reporter:<br />
                    <span style="font-size:small; font-weight:normal;">Choose from the list of people or add in your details</span>
                </th>
                <td valign="top" style="width:560px;">
                    <p>
                        <input type="radio" name="agent-new-existing" value="existing" checked="checked" /> Existing <strong>or</strong>
                        <input type="radio" name="agent-new-existing" value="new" /> New
                    </p>

                    <div id="agent-existing-value" style="width:300px;">''' + get_agents_dropdown(get_agents()[1]) + '''</div>
                    <div id="agent-new-value" style="width:300px; display:none;">
                        <table class="layout">
                            <tr><td>Name:</td><td><input id="agent-name" name="agent-name" type="text" /></td></tr>
                            <tr><td>URI:</td><td><input id="agent-uri" name="agent-uri" type="text" /></td></tr>
                            <tr><td>Email:</td><td><input id="agent-email" name="agent-email" type="text" /></td></tr>
                        </table>
                    </div>
                </td>
            </tr>
            <tr><td colspan="2"><h3>Report</h3></td></tr>
            <tr>
                <th>
                    Report Type:<br />
                    <span style="font-size:small; font-weight:normal;">Only <a href="http://www.promsns.org/ns/proms#BasicReport" class="definition">Basic</a> and <a href="http://www.promsns.org/ns/proms#ExternalReport" class="definition">External</a> <em>Reports</em> are allowed using this form.</span></th>
                <td valign="top">
                    <select name="report-type" id="report-type">
                        <option value="BasicReport">Basic</option>
                        <option value="ExternalReport">External</option>
                    </select>
                </td>
            </tr>
            <tr><th>Report Title:<br /><span style="font-size:small; font-weight:normal;">A simple title for the <em>Report</em>. Can be the same for multiple <em>Reports</em> where systems are reporting multiple times.</span></th><td><input type="text" name="report-title" id="report-title" /></td></tr>
            <tr>
                <th>
                    Reporting System:<br />
                    <span style="font-size:small; font-weight:normal;">You must have already registered a <a href="http://www.promsns.org/ns/proms#ReportingSystem" class="definition">Reporting System</a> for this <em>Report</em>. See the <a style="text-decoration:line-through;" href="/function/register_reporting_system">Reporting System registration</a> page.</span>
                </th>
                <td>
                ''' + get_reportingsystems_dropdown(get_reportingsystems()[1]) + '''
                </td>
            </tr>
            <tr>
                <th>Native ID:<br /><span style="font-size:small; font-weight:normal;">An ID for this <em>Report</em> assigned by the system you are reporting for. If no ID can be known (e.g. for a manual process), use the word "none".</span></th>
                <td><input type="text" name="report-nativeId" id="report-nativeId" /></td>
            </tr>
            <tr><td colspan="2"><h3>Activity</h3></td></tr>
            <tr>
                <th>Activity Title:<br /><span style="font-size:small; font-weight:normal;">A simple title for the <em>Activity</em>. Try to use something different from the Report Title.</span></th>
                <td><input type="text" name="activity-title" id="activity-title" /></td>
            </tr>
            <tr>
                <th>Activity Description:<br /><span style="font-size:small; font-weight:normal;">A simple description for the <em>Activity</em>.</span></th>
                <td><textarea name="activity-description" id="activity-description" style="width:230px;"></textarea></td>
            </tr>
            <tr>
                <th>Activity Started At Time:<br /><span style="font-size:small; font-weight:normal;">The time at which the <em>Activity</em> started.</span></th>
                <td><input type="text" name="activity-startedAtTime" id="activity-startedAtTime" /></td>
            </tr>
            <tr>
                <th>Activity Ended At Time:<br /><span style="font-size:small; font-weight:normal;">The time at which the <em>Activity</em> ended.</span></th>
                <td><input type="text" name="activity-endedAtTime" id="activity-endedAtTime" /></td>
            </tr>
            <tr><td colspan="2"><h3>Entities</h3></td></tr>
            <tr>
                <th>
                    Entity Used:<br />
                    <span style="font-size:small; font-weight:normal;">Choose from the list of <em>Entities</em> known to this PROMS instance or add in your own details</span>
                </th>
                <td valign="top">
                    <table class="entity layout" id="entity-inputs">
                        <tr id="entity-input-row-01">
                            <td>
                                <input type="radio" class="entity-used-new-existing" name="entity-01-new-existing" value="existing" checked="checked" /> Existing <strong>or</strong>
                                <input type="radio" class="entity-used-new-existing" name="entity-01-new-existing" value="new" /> New
                            </td>
                            <td><input type="text" class="entity-input" name="entity-input-01" id="entity-input-01" /></td>
                            <td><span class="entity-input-delete" id="entity-input-delete-01">delete</span></td>
                        </tr>
                        <tr id="entity-input-row-add">
                            <td></td>
                            <td></td>
                            <td><span class="entity-input-add">add another</span></td>
                        </tr>
                    </table>

                    <!--
                    <p>
                        <input type="radio" name="entity-01-new-existing" value="existing" checked="checked" /> Existing <strong>or</strong>
                        <input type="radio" name="entity-01-new-existing" value="new" /> New
                    </p>

                    <div id="entity-01-existing-value" style="width:300px;">
                        <select name="entity-01" id="entity-01">
                        ''' + get_entities_dropdown(get_entities()[1]) + '''
                        </select>
                    </div>
                    <div id="entity-01-new-value" style="width:300px; display:none;">
                        <table class="layout">
                            <tr><td>Title:</td><td><input id="entity-01-title" name="entity-01-title" type="text" /></td></tr>
                            <tr><td>URI:</td><td><input id="entity-01-uri" name="entity-01-uri" type="text" /></td></tr>
                            <tr><td>Value:</td><td><input id="entity-01-value" name="entity-01-value" type="text" /></td></tr>
                        </table>
                    </div>
                    -->
                </td>
            </tr>
            <tr>
                <th colspan="3" style="text-align:right;">
                    <br />
                    <button id="generate-report">Generate Report</button><br />
                    <textarea id="generated-results" style="display:none; width:840px;"></textarea>
                    <button id="generate-report" style="display:none;">Store Report Here</button>
                </th>
            </tr>
        </table>
    </form>
    '''
    html += get_proms_html_footer()

    return html


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

    html = get_proms_html_header()
    html += '''
    <h1>Provenance Management Service</h1>
    <h2>Register a <em>Reporting System</em></h2>
    <h3 style="color:red; font-style:italic;">Coming!</h3>
    '''
    html += get_proms_html_footer()

    return html
