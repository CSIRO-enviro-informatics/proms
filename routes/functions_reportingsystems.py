import urllib
import functions_sparqldb


def get_reportingsystems_dict():
    """ Get all ReportingSystem details
    """
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?rs ?t
        WHERE {
          ?rs a proms:ReportingSystem .
          ?rs rdfs:label ?t .
        }
    '''
    reportingsystems = functions_sparqldb.query(query)
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
    """ Get details for a ReportingSystem
    """
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        SELECT ?t ?fn ?o ?em ?ph ?add ?v
        WHERE {
          <''' + reportingsystem_uri + '''> a proms:ReportingSystem .
          <''' + reportingsystem_uri + '''> rdfs:label ?t .
          OPTIONAL { <''' + reportingsystem_uri + '''> proms:owner ?o . }
          OPTIONAL { <''' + reportingsystem_uri + '''> proms:validation ?v . }
          OPTIONAL { ?o vcard:fn ?fn . }
          OPTIONAL { ?o vcard:hasEmail ?em . }
          OPTIONAL { ?o vcard:hasTelephone ?ph_1 . }
          OPTIONAL { ?ph_1 vcard:hasValue ?ph . }
          OPTIONAL { ?o vcard:hasAddress ?add_1 . }
          OPTIONAL { ?add_1 vcard:locality ?add }
        }
    '''
    reportingsystem_detail = functions_sparqldb.query(query)
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
            if 'v' in reportingsystem_detail['results']['bindings'][0]:
                ret['v'] = reportingsystem_detail['results']['bindings'][0]['v']['value']
            ret['uri'] = reportingsystem_uri

            svg_script = get_reportingsystem_details_svg(ret)
            if svg_script[0] == True:
                rs_script = svg_script[1]
                rs_script += get_reportingsystem_reports_svg(reportingsystem_uri)
                ret['rs_script'] = rs_script
    return ret


def get_reports_for_rs_query(reportingsystem_uri):
    """ Construct a query to get all Reports for the specified ReportingSystem
    """
    query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
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
        ?r rdfs:label ?t .
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
    """ Get all Reports for a ReportingSystem
    """
    query = get_reports_for_rs_query(reportingsystem_uri)
    return functions_sparqldb.query(query)


def get_reportingsystem_details_svg(reportingsystem_dict):
    """ Construct the SVG code for the ReportingSystem
    """
    rLabel = reportingsystem_dict.get('t', 'Untitled')
    script = '''
        var rLabel = "''' + rLabel + '''";
        var reportingSystem = addReportingSystem(35, 5, rLabel, "", "");
    '''
    return [True, script]


def get_reportingsystem_reports_svg(reportingsystem_uri):
    """ Construct SVG code for all Reports contained in a ReportingSystem
    """
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
                var report0 = addReport(''' + str(x_pos) + ''', ''' + str(y_top) + ''', "''' + r1title + '''", "''' + settings.WEB_SUBFOLDER + "/id/report/?uri=" + r1uri_encoded + '''", "''' + r1jobId + '''");
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
                            var report = addReport(''' + str(x_pos) + ''', ''' + str(y_offset) + ''', "Multiple Reports, click to search", "''' + settings.WEB_SUBFOLDER + "/function/sparql/?query=" + query_encoded + '''");
                            reports.push(report);
                        '''
                        break
                    uri = report['r']['value']
                    uri_encoded = urllib.quote(uri);
                    title = report['t']['value']
                    jobId = report['job']['value']
                    reports_script += '''
                        var report = addReport(''' + str(x_pos) + ''', ''' + str(y_offset) + ''', "''' + title + '''", "''' + settings.WEB_SUBFOLDER + "/id/report/?uri=" + uri_encoded + '''", "''' + jobId + '''");
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
            //var reportUsedFaultText = addReport(550, 200, "There is a fault with retrieving Reports that may have used this ReportingSystem", "");
            var reportUsedFaultText = addReport(550, 0, "No Reports for this RS", "");
        '''
    return reports_script


def put_reportingsystem(reportingsystem_in_turtle):
    """ Add a ReportingSystem to PROMS
    """
    try:
        # try to make a graph of the input text
        g = Graph().parse(cStringIO.StringIO(reportingsystem_in_turtle), format='turtle')

        # validate
        v = ReportingSytems(g)
        # fail if RuleSet validation unsuccessful
        if not v.passed:
            return [False, v.fail_reasons]

        # replace the document's placeholder URI with one generated by this PROMS instance
        g = replace_placeholder_uuids(g)

        # get the ReportingSystem URI
        result = g.query('''
            PREFIX proms: <http://promsns.org/def/proms#>
            SELECT ?rs WHERE {
                ?rs a proms:ReportingSystem .
            }
        ''')
        for row in result:
            rs_uri = row[0]

        # insert into triplestore's default graph
        insert = functions_sparqldb.insert(g)
        if insert[0]:
            return [insert[0], [rs_uri]]
        else:
            return insert
    except Exception as e:
        return [False, ['Could not parse input: ' + str(e)]]
