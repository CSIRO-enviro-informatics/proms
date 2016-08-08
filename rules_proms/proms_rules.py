__author__ = 'ayr016'


has_report = '''
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?s
        WHERE {
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
        }
        '''


has_generatedAtTime = '''
        PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        ASK
        WHERE {
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s prov:generatedAtTime ?t .
        }
        '''


has_label = '''
		PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?s
        WHERE {
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  rdfs:label     ?t .
        }
		'''


reporting_system_has_label = '''
		PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        ASK
        WHERE {
            ?s  a            proms:ReportingSystem .
            ?s  rdfs:label     ?t .
        }
		'''


reporting_system_has_validation = '''
		PREFIX proms: <http://promsns.org/def/proms#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        ASK
        WHERE {
            ?s  a            proms:ReportingSystem .
            ?s  proms:validation     ?t .
        }
		'''


has_nativeId = '''
		PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?s
        WHERE {
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  proms:nativeId  ?j .
        }
		'''


has_reportingSystem = '''
        PREFIX proms: <http://promsns.org/def/proms#>
        ASK
        WHERE {
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  proms:reportingSystem  ?rs .
        }
		'''


get_reportingSystem = '''
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?rs
        WHERE {
            { ?s  a            proms:BasicReport .}
            UNION
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  proms:reportingSystem  ?rs .
        }
		'''


## is the reporting system registered on the server?
## needs .format(id of reporting system)
def has_registered_reportingSystem(name):
	return 	('''
	PREFIX proms: <http://promsns.org/def/proms#>
	ASK
	WHERE {<''' + name + '''> a proms:ReportingSystem.
        }
	''')


has_startingActivity = '''
		PREFIX proms: <http://promsns.org/def/proms#>
		PREFIX prov: <http://www.w3.org/ns/prov#>
        ASK
        WHERE {
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  proms:startingActivity  ?rs .
            ?rs a prov:Activity .
        }
		'''

has_endingActivity = '''
		PREFIX proms: <http://promsns.org/def/proms#>
		PREFIX prov: <http://www.w3.org/ns/prov#>
        ASK
        WHERE {
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            ?s  proms:endingActivity  ?rs .
            ?rs a prov:Activity .
        }
		'''

are_startingActivityAndEndingActivityTheSame = '''
		PREFIX proms: <http://promsns.org/def/proms#>
		PREFIX prov: <http://www.w3.org/ns/prov#>
        ASK
        WHERE {
            ?s a proms:ExternalReport .
            ?s proms:startingActivity ?sa .
            ?s proms:endingActivity ?sa .
        }
		'''

are_startingActivityAndEndingActivityDifferent = '''
		PREFIX proms: <http://promsns.org/def/proms#>
		PREFIX prov: <http://www.w3.org/ns/prov#>
        ASK
        WHERE {
            ?s a proms:InternalReport .
            ?s proms:startingActivity ?sa .
            ?s proms:endingActivity ?ea .
            FILTER (?sa != ?ea)
        }
		'''

used_entity = '''
		PREFIX proms: <http://promsns.org/def/proms#>
		PREFIX prov: <http://www.w3.org/ns/prov#>
        ASK
        WHERE {
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            { ?s proms:startingActivity ?act . }
            UNION
            { ?s proms:endingActivity ?act . }
            ?act prov:used ?e1.
            ?e1 a prov:Entity.
        }
'''

generated_entity = '''
		PREFIX proms: <http://promsns.org/def/proms#>
		PREFIX prov: <http://www.w3.org/ns/prov#>
        ASK
        WHERE {
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            { ?s proms:startingActivity ?act . }
            UNION
            { ?s proms:endingActivity ?act . }
            ?act prov:generated ?e1.
            ?e1 a prov:Entity.
        }
'''

used_entityNotGenerated = '''
		PREFIX proms: <http://promsns.org/def/proms#>
		PREFIX prov: <http://www.w3.org/ns/prov#>
        ASK
        WHERE {
            { ?s  a            proms:ExternalReport .}
            UNION
            { ?s  a            proms:InternalReport .}
            { ?s proms:startingActivity ?act . }
            UNION
            { ?s proms:endingActivity ?act . }
            ?act prov:used ?e1.
            ?act prov:generated ?e2.
            FILTER (?e1 != ?e2)
        }
'''

started_startActivityBeforeEndActivity = '''
		PREFIX proms: <http://promsns.org/def/proms#>
		PREFIX prov: <http://www.w3.org/ns/prov#>
        ASK
        WHERE {
			?s  a            proms:InternalReport .
			?s proms:startingActivity ?sa .
			?s proms:endingActivity ?ea .
			?sa prov:startedAtTime ?st .
			?ea prov:startedAtTime ?et .
			FILTER (?et > ?st)
		}
'''