import cStringIO
import uuid
from rdflib import Graph
import settings





def replace_placeholder_uuids(g):
    """ Replace any placholder URIs ('http://placeholder.org') with URIs from settings.py specific to the RDF type
    """
    # Reporting Systems
    q = '''
    PREFIX proms: <http://promsns.org/def/proms#>
    SELECT ?s
    WHERE {
        ?s a proms:ReportingSystem .
    }
    '''
    for row in g.query(q):
        replace_uri(g, str(row[0]), settings.REPORTINGSYSTEM_BASE_URI + '/' + str(uuid.uuid4()))

    #
    report_uuid = str(uuid.uuid4())
    q = '''
    PREFIX proms: <http://promsns.org/def/proms#>
    SELECT ?s
    WHERE {
        { ?s a proms:BasicReport . }
        UNION
        { ?s a proms:ExternalReport . }
        UNION
        { ?s a proms:InternalReport . }
    }
    '''
    for row in g.query(q):
        replace_uri(g, str(row[0]), settings.REPORT_BASE_URI + '/' + report_uuid)

    # find all the Activity and locally-defined (hash) Entity URIs and replace them too
    q = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    SELECT ?s
    WHERE {
        ?s a prov:Activity .
        FILTER (STRSTARTS(STR(?s), "http://placeholder.org"))
    }
    '''
    for row in g.query(q):
        replace_uri(g, str(row[0]), settings.ACTIVITY_BASE_URI + '/' + report_uuid + str(row[0]).split('#')[1])

    q = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    SELECT ?s
    WHERE {
        {?s a prov:Entity . }
        UNION
        {?s a prov:Plan . }
        FILTER (STRSTARTS(STR(?s), "http://placeholder.org"))
    }
    '''
    for row in g.query(q):
        replace_uri(g, str(row[0]), settings.ENTITY_BASE_URI + '/' + report_uuid + str(row[0]).split('#')[1])

    return g

