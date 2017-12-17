import logging
from pingbacks.strategies import strategy_functions


PREFIXES = '''
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix xml: <http://www.w3.org/XML/1998/namespace> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
            @prefix pns-data: <http://promsns.org/eg/entity-server/id/dataset/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix prov: <http://www.w3.org/ns/prov#> .
        '''

# data from http://promsns.org/eg/entity-server/id/dataset/
DATA = [
    {
        'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/001',
        'rdf_metadata': '''
                        pns-data:001 a dcat:Dataset, prov:Entity ;
                            dct:description "No pingback or provenance properties"^^xsd:string ;
                            dct:isPartOf <http://promsns.org/eg/entity-server/id/dataset> ;
                            dct:title "Dataset 001"^^xsd:string
                        .
                        '''
    },
    {
        'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/002',
        'rdf_metadata': '''
                        pns-data:002 a dcat:Dataset, prov:Entity ;
                            dct:description "has_provenance property only"^^xsd:string ;
                            dct:isPartOf <http://promsns.org/eg/entity-server/id/dataset> ;
                            dct:title "Dataset 002"^^xsd:string ;
                            dct:has_provenance <http://promsns.org/eg/entity-server/id/bundle/x>
                        .
                        '''
    },
    {
        'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/003',
        'rdf_metadata': '''
                        pns-data:003 a dcat:Dataset, prov:Entity ;
                            dct:description "has_query_service property only"^^xsd:string ;
                            dct:isPartOf <http://promsns.org/eg/entity-server/id/dataset> ;
                            dct:title "Dataset 003"^^xsd:string ;
                            prov:has_query_service <http://promsns.org/eg/entity-server/api/provenance-service>
                        .
                        '''
    },
    {
        'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/004',
        'rdf_metadata': '''
                        pns-data:004 a dcat:Dataset, prov:Entity ;
                            dct:description "pingback property only"^^xsd:string ;
                            dct:isPartOf <http://promsns.org/eg/entity-server/id/dataset> ;
                            dct:title "Dataset 004"^^xsd:string ;
                            prov:pingback <http://example.com/id/bundle/y>
                        .
                        '''
    },
    {
        'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/005',
        'rdf_metadata': '''
                        pns-data:005 a dcat:Dataset, prov:Entity ;
                            dct:description "has_provenance, has_query_service & pingback properties"^^xsd:string ;
                            dct:isPartOf <http://promsns.org/eg/entity-server/id/dataset> ;
                            dct:title "Dataset 005"^^xsd:string ;
                            prov:has_provenance <http://example.com/id/bundle/y> ;
                            prov:has_query_service <http://promsns.org/eg/entity-server/api/provenance-service> ;
                            prov:pingback <http://promsns.org/eg/entity-server/api/pingback-service/dataset/005> ,
                                <http://promsns.org/eg/entity-server/api/pingback-service2/dataset/005>
                        .
                        '''
    },
    {
        'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/006',
        'rdf_metadata': '''
                        <http://example.com/metadata/1> a dcat:CatalogRecord, prov:Entity ;
                            prov:pingback <http://promsns.org/eg/entity-server/api/pingback-service/dataset/006> ;
                            foaf:primaryTopic pns-data:006
                        .

                        pns-data:006 a dcat:Dataset, prov:Entity ;
                            dct:description "Has a dcat:CatalogRecord with a prov:pingback property"^^xsd:string ;
                            dct:title "Dataset 006"^^xsd:string
                        .
                        '''
    },
    {
        'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/007',
        'rdf_metadata': '''
                        <http://example.com/metadata/1> a dcat:CatalogRecord, prov:Entity ;
                            prov:has_query_service <http://promsns.org/eg/entity-server/api/provenance-service> ;
                            foaf:primaryTopic pns-data:007
                        .

                        pns-data:007 a dcat:Dataset, prov:Entity ;
                            dct:description "Has a dcat:CatalogRecord with a prov:pingback property"^^xsd:string ;
                            dct:title "Dataset 006"^^xsd:string
                        .
                        '''
    }
]


def test_is_dereferencable():
    # test a 200 response - HTML
    r = strategy_functions.is_dereferencable('http://promsns.org')
    a = r[0] and 'text/html' in r[2]['Content-Type']

    # test a 200 response - RDF
    r = strategy_functions.is_dereferencable('http://promsns.org/eg/entity-server/id/dataset/001')
    b = r[0] and 'text/turtle' in r[2]['Content-Type']

    # test a 404 response
    r = strategy_functions.is_dereferencable('http://promsns.org/eg/entity-server/id/dataset/999')
    c = not r[0]

    # test a non-dereferenacable response
    r = strategy_functions.is_dereferencable('http://broken_link.com/resource/1')
    d = not r[0]

    return a and b and c and d


def test_has_valid_rdf_meatadata_true():
    metadata = PREFIXES + '''
        pns-data:002 a dcat:Dataset, prov:Entity ;
            dct:description "has_provenance property only"^^xsd:string ;
            dct:isPartOf <http://promsns.org/eg/entity-server/id/dataset> ;
            dct:title "Dataset 002"^^xsd:string ;
            prov:has_provenance <http://promsns.org/eg/entity-server/id/bundle/x>
        .
     '''
    headers = 'text/turtle'
    return strategy_functions.has_valid_rdf_meatadata(metadata, headers)[0]


def test_has_valid_rdf_meatadata_false():
    # missing a final '.' after last line
    metadata = PREFIXES + '''
        pns-data:002 a dcat:Dataset, prov:Entity ;
            dct:description "has_provenance property only"^^xsd:string ;
            dct:isPartOf <http://promsns.org/eg/entity-server/id/dataset> ;
            dct:title "Dataset 002"^^xsd:string ;
            prov:has_provenance <http://promsns.org/eg/entity-server/id/bundle/x>
     '''
    headers = 'text/turtle'
    return not strategy_functions.has_valid_rdf_meatadata(metadata, headers)[0]


def test_get_pingback_endpoints_via_given():
    entity_uri = 'http://example.com/resource/1'
    ttl = PREFIXES + '''
        <''' + entity_uri + '''> a dcat:Dataset, prov:Entity ;
            dct:description "has_provenance property only"^^xsd:string ;
            dct:title "Dataset 002"^^xsd:string ;
            prov:pingback <http://example.com/resource/1/pingback> ,
                <http://example.com/resource/1/pingback/2>
        .
        '''
    expected_results = ['http://example.com/resource/1/pingback', 'http://example.com/resource/1/pingback/2'].sort()
    actual_results = strategy_functions.get_pingback_endpoints_via_given(strategy_functions.get_graph(ttl), entity_uri).sort()

    ttl2 = PREFIXES + '''
        <''' + entity_uri + '''> a dcat:Dataset, prov:Entity ;
            dct:description "has_provenance property only"^^xsd:string ;
            dct:title "Dataset 002"^^xsd:string
        .
        '''
    expected_results2 = []
    actual_results2 = strategy_functions.get_pingback_endpoints_via_given(strategy_functions.get_graph(ttl2), entity_uri)  # cannot sort []

    return actual_results == expected_results and actual_results2 == expected_results2


def test_get_has_query_service_endpoints_via_given():
    entity_uri = 'http://example.com/resource/1'
    ttl = PREFIXES + '''
        <''' + entity_uri + '''> a dcat:Dataset, prov:Entity ;
            dct:description "has_provenance property only"^^xsd:string ;
            dct:title "Dataset 002"^^xsd:string ;
            prov:has_query_service <http://example.com/resource/1/pingback> ,
                <http://example.com/resource/1/pingback/2>
        .
        '''
    expected_results = ['http://example.com/resource/1/pingback', 'http://example.com/resource/1/pingback/2']
    expected_results.sort()
    actual_results = strategy_functions.get_has_query_service_endpoints_via_given(strategy_functions.get_graph(ttl), entity_uri)
    actual_results.sort()

    ttl2 = PREFIXES + '''
        <''' + entity_uri + '''> a dcat:Dataset, prov:Entity ;
            dct:description "has_provenance property only"^^xsd:string ;
            dct:title "Dataset 002"^^xsd:string
        .
        '''
    expected_results2 = []
    actual_results2 = strategy_functions.get_has_query_service_endpoints_via_given(strategy_functions.get_graph(ttl2), entity_uri)  # cannot sort []

    return actual_results == expected_results and actual_results2 == expected_results2


def test_get_pingback_endpoints_via_lookup():
    expected_results = [
        {
            'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/004',
            'enpoints': ['http://example.com/id/bundle/y']
        },
        {
            'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/005',
            'enpoints': [
                            'http://promsns.org/eg/entity-server/api/pingback-service/dataset/005',
                            'http://promsns.org/eg/entity-server/api/pingback-service2/dataset/005'
            ]
        },
        {
            'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/006',
            'enpoints': ['http://promsns.org/eg/entity-server/api/pingback-service/dataset/006']
        }
    ]

    actual_results = []
    for datum in DATA:
        r = strategy_functions.get_pingback_endpoints_via_lookup(strategy_functions.get_graph(PREFIXES + datum['rdf_metadata']), datum['entity_uri'])
        if len(r) > 0:
            r.sort()
            actual_results.append({
                'entity_uri': datum['entity_uri'],
                'enpoints': r
            })

    return actual_results == expected_results


def test_get_has_provenance_service_endpoints_via_lookup():
    expected_results = [
        {
            'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/003',
            'enpoints': ['http://promsns.org/eg/entity-server/api/provenance-service']
        },
        {
            'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/005',
            'enpoints': ['http://promsns.org/eg/entity-server/api/provenance-service']
        },
        {
            'entity_uri': 'http://promsns.org/eg/entity-server/id/dataset/007',
            'enpoints': ['http://promsns.org/eg/entity-server/api/provenance-service']
        }
    ]

    actual_results = []
    for datum in DATA:
        r = strategy_functions.get_has_query_service_endpoints_via_lookup(strategy_functions.get_graph(PREFIXES + datum['rdf_metadata']), datum['entity_uri'])
        if len(r) > 0:
            r.sort()
            actual_results.append({
                'entity_uri': datum['entity_uri'],
                'enpoints': r
            })

    return actual_results == expected_results


def test_send_pingback():
    # test against the pingback service on the Entity Server
    pingback_test_uri = 'http://promsns.org/eg/entity-server/api/pingback-service/dataset/001'
    pingback_test_uri = 'http://localhost:8010/api/pingback-service/dataset/001'
    fake_provenance_uris = [
        '# this is a comment',
        'http://example.com/a/b/c',
        'http://example.com/d/e/f',
        'http://example.com/g/h/i',
        'http://example.com/j/k/l',
        'http://example.com/m/n/o',
    ]
    r1 = strategy_functions.send(pingback_test_uri, fake_provenance_uris)[0]

    # test a broken URI
    r2 = not strategy_functions.send(pingback_test_uri, 'not_a_uri')[0]

    # test empty messages
    r3 = not strategy_functions.send(pingback_test_uri, [])[0]
    r4 = not strategy_functions.send(pingback_test_uri, '')[0]

    # test further_links - pass
    further_links_example = [
        {
            'resource': 'http://example.com/g/h/i',
            'rel': 'has_provenance',
            'anchor': 'http://example.com/resource'
        },
        {
            'resource': 'http://example.com/j/k/l',
            'rel': 'has_query_service',
            'anchor': 'http://example.com/endpoint1'
        },
        {
            'resource': 'http://example.com/m/n/o',
            'rel': 'has_query_service',
            'anchor': 'http://example.com/endpoint2'
        }
    ]
    r5 = strategy_functions.send(pingback_test_uri, fake_provenance_uris, further_links_example)[0]

    '''
    # test further_links - fail, Exception raised
    further_links_example = [
        {
            'resource': 'http://example.com/g/h/i/x',
            'rel': 'has_provenance',
            'anchor': 'http://example.com/resource'
        }
    ]
    r6 = functions.send_pingback(pingback_test_uri, fake_provenance_uris,further_links_example)[0]
    '''

    '''
    # test further_links - fail, Exception raised
    further_links_example = [
        {
            'resource': 'http://example.com/g/h/i',
            'rel': 'has_provenance',
            'anchor': 'www.example.com/resource'
        }
    ]
    r7 = functions.send_pingback(pingback_test_uri, fake_provenance_uris,further_links_example)[0]
    '''

    return r1 and r2 and r3 and r4 and r5


def test_send_bundle():
    pass


if __name__ == "__main__":
    logging.basicConfig()
    print(test_is_dereferencable())
    print(test_has_valid_rdf_meatadata_true())
    print(test_has_valid_rdf_meatadata_false())
    print(test_get_pingback_endpoints_via_given())
    print(test_get_pingback_endpoints_via_lookup())
    print(test_get_has_query_service_endpoints_via_given())
    print(test_get_has_provenance_service_endpoints_via_lookup())
    print(test_send_pingback())
