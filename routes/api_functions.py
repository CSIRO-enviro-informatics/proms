import cStringIO
import json
import urllib
from flask import Response, render_template
from rdflib import Graph, Namespace, Literal, URIRef, RDF, XSD, BNode
import settings
from database import queries
from modules.ldapi import LDAPI


def get_sparql_service_description(rdf_format='turtle'):
    """Return an RDF description of PROMS' read only SPARQL endpoint in a requested format

    :param rdf_format: 'turtle', 'n3', 'xml', 'json-ld'
    :return: string of RDF in the requested format
    """
    sd_ttl = '''
        @prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix sd:     <http://www.w3.org/ns/sparql-service-description#> .
        @prefix sdf:    <http://www.w3.org/ns/formats/> .
        @prefix void: <http://rdfs.org/ns/void#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        <%(BASE_URI)s/function/sparql>
            a                       sd:Service ;
            sd:endpoint             <%(BASE_URI)s/function/sparql> ;
            sd:supportedLanguage    sd:SPARQL11Query ; # yes, read only, sorry!
            sd:resultFormat         sdf:SPARQL_Results_JSON ;  # yes, we only deliver JSON results, sorry!
            sd:feature sd:DereferencesURIs ;
            sd:defaultDataset [
                a sd:Dataset ;
                sd:defaultGraph [
                    a sd:Graph ;
                    void:triples "100"^^xsd:integer
                ]
            ]
        .
    ''' % {'BASE_URI': settings.BASE_URI}
    g = Graph().parse(cStringIO.StringIO(sd_ttl), format='turtle')
    rdf_formats = list(set([x[1] for x in LDAPI.MIMETYPES_PARSERS]))
    if rdf_format[0][1] in rdf_formats:
        return g.serialize(format=rdf_format[0][1])
    else:
        raise ValueError('Input parameter rdf_format must be one of: ' + ', '.join(rdf_formats))


def replace_uri(g, initial_uri, replacement_uri):
    """
    Replaces a given URI for all subjects or objects (not predicates) in a given graph

    :param g: the graph to replace URIs in
    :param initial_uri: the URI to replace
    :param replacement_uri: the replacement URI
    :return: the altered graph g
    """
    # replace all subjects
    u = '''
        DELETE {
            ?s ?p ?o .
        }
        INSERT {
            <%(replacement_uri)s> ?p ?o .
        }
        WHERE {
            ?s ?p ?o .
            FILTER (STR(?s) = "%(initial_uri)s")
            # Nick: this really seems to need to be a FILTER, not a subgraph match i.e. <> ?p ?o . Don't know why.
        }
    ''' % {'replacement_uri': replacement_uri, 'initial_uri': initial_uri}
    g.update(u)

    # replace all objects
    u = '''
        DELETE {
            ?s ?p ?o .
        }
        INSERT {
            ?s ?p <%(replacement_uri)s> .
        }
        WHERE {
            ?s ?p ?o .
            FILTER (STR(?o) = "%(initial_uri)s")
        }
    ''' % {'replacement_uri': replacement_uri, 'initial_uri': initial_uri}
    g.update(u)

    # there are no predicates to place (no placeholder relations)
    return g


def client_error_response(error_message):
    """Returns a themed HTML page with an status code of 400 (Bad Request)"""
    return Response(
        error_message,
        status=400,
        mimetype='text/plain'
    )


def server_error_response(error_message):
    """Returns a themed HTML page with an status code of 500 (Server Error)"""
    return Response(
        error_message,
        status=500,
        mimetype='text/plain'
    )


def render_alternates_view(class_uri, class_uri_encoded, instance_uri, instance_uri_encoded, views_formats, mimetype):
    """Renders an HTML table, a JSON object string or a serialised RDF representation of the alternate views of an
    object"""
    if mimetype == 'application/json':
        del views_formats['renderer']  # the renderer used is not for public consumption!
        return Response(json.dumps(views_formats), status=200, mimetype='application/json')
    elif mimetype in LDAPI.get_rdf_mimetypes_list():
        g = Graph()
        LDAPI_O = Namespace('http://promsns.org/def/ldapi#')
        g.bind('ldapi', LDAPI_O)
        DCT = Namespace('http://purl.org/dc/terms/')
        g.bind('dct', DCT)

        class_uri_ref = URIRef(urllib.unquote_plus(class_uri))

        if instance_uri:
            instance_uri_ref = URIRef(instance_uri)
            g.add((instance_uri_ref, RDF.type, class_uri_ref))
        else:
            g.add((class_uri_ref, RDF.type, LDAPI_O.ApiResource))

        # alternates model
        alternates_view = BNode()
        g.add((alternates_view, RDF.type, LDAPI_O.View))
        g.add((alternates_view, DCT.title, Literal('alternates', datatype=XSD.string)))
        g.add((class_uri_ref, LDAPI_O.view, alternates_view))

        # default model
        default_view = BNode()
        g.add((default_view, DCT.title, Literal('default', datatype=XSD.string)))
        g.add((class_uri_ref, LDAPI_O.defaultView, default_view))
        default_title = views_formats['default']

        # the ApiResource is incorrectly assigned to the class URI
        for view_name, formats in views_formats.iteritems():
            if view_name == 'alternates':
                for f in formats:
                    g.add((alternates_view, URIRef('http://purl.org/dc/terms/format'), Literal(f, datatype=XSD.string)))
            elif view_name == 'default':
                pass
            elif view_name == 'renderer':
                pass
            else:
                x = BNode()
                if view_name == default_title:
                    g.add((default_view, RDF.type, x))
                g.add((class_uri_ref, LDAPI_O.view, x))
                g.add((x, DCT.title, Literal(view_name, datatype=XSD.string)))
                for f in formats:
                    g.add((x, URIRef('http://purl.org/dc/terms/format'), Literal(f, datatype=XSD.string)))


        # make the static part of the graph
        # REG = Namespace('http://purl.org/linked-data/registry#')
        # self.g.bind('reg', REG)
        #
        # self.g.add((URIRef(self.request.url), RDF.type, REG.Register))
        #
        # # add all the items
        # for item in self.register:
        #     self.g.add((URIRef(item['uri']), RDF.type, URIRef(self.uri)))
        #     self.g.add((URIRef(item['uri']), RDFS.label, Literal(item['label'], datatype=XSD.string)))
        #     self.g.add((URIRef(item['uri']), REG.register, URIRef(self.request.url)))
        rdflib_format = [item[1] for item in LDAPI.MIMETYPES_PARSERS if item[0] == mimetype][0]
        return Response(g.serialize(format=rdflib_format), status=200, mimetype=mimetype)
    else:  # HTML
        return render_template(
            'alternates_view.html',
            class_uri=class_uri,
            class_uri_encoded=class_uri_encoded,
            instance_uri=instance_uri,
            instance_uri_encoded=instance_uri_encoded,
            views_formats=views_formats
        )


def get_agents():
    """ Get all Agents in the provenance database"""

    q = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?ag ?label
        WHERE { GRAPH ?g {
            ?ag a prov:Agent ;
                rdfs:label ?label .
          }
        }
        '''
    agents = []
    for row in queries.query(q)['results']['bindings']:
        agents.append({
            'uri': row['ag']['value'],
            'label': row['label']['value']
        })

    return agents


def get_reportingsystems():
    """ Get all ReportingSystem details"""
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT ?rs ?t
        WHERE {
          ?rs a proms:ReportingSystem .
          ?rs rdfs:label ?t .
        }
    '''
    reportingsystems = queries.query(query)
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


def get_entities():
    """ Get details for all Entities
    """
    query = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX proms: <http://promsns.org/def/proms#>
        SELECT DISTINCT ?e ?l
        WHERE {
            GRAPH ?g {
                { ?e a prov:Entity . }
                UNION
                { ?e a prov:Plan . }
                OPTIONAL { ?e rdfs:label ?l . }
            }
        }
        ORDER BY ?e
    '''
    entities = queries.query(query)
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