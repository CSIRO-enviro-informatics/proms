from rdflib import Graph
import cStringIO
from ldapi import LDAPI
import settings


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

        <''' + settings.BASE_URI + '/function/sparql' + '''>
            a                       sd:Service ;
            sd:endpoint             <''' + settings.BASE_URI + '/function/sparql' + '''> ;
            sd:supportedLanguage    sd:SPARQL11Query ; # yes, read only, sorry!
            sd:resultFormat         sdf:SPARQL_Results_JSON ; # yes, we only deliver JSON results, sorry!
            sd:feature sd:DereferencesURIs ;
            sd:defaultDataset [
                a sd:Dataset ;
                sd:defaultGraph [
                    a sd:Graph ;
                    void:triples "100"^^xsd:integer
                ]
            ]
        .
    '''
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
            <''' + replacement_uri + '''> ?p ?o .
        }
        WHERE {
            ?s ?p ?o .
            FILTER (STR(?s) = "''' + initial_uri + '''")
            # Nick: this really seems to need to be a FILTER, not a subgraph match i.e. <> ?p ?o . Don't know why.
        }
    '''
    g.update(u)

    # replace all objects
    u = '''
        DELETE {
            ?s ?p ?o .
        }
        INSERT {
            ?s ?p <''' + replacement_uri + '''> .
        }
        WHERE {
            ?s ?p ?o .
            FILTER (STR(?o) = "''' + initial_uri + '''")
        }
    '''
    g.update(u)

    # there are no predicates to place (no placeholder relations)
    return g
