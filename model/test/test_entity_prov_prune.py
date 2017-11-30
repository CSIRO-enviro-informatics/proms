from rdflib import Graph, Namespace, RDF, RDFS
import rdflib.compare

# er = EntityRenderer('', None)
#
# # g = Graph().parse('test_entity_prov_network.ttl', format='turtle')
# # terget_entity = 'http://test.com#E03'
# g = Graph().parse('test_entity_prov_two_ext_reports.ttl', format='turtle')
# target_entity = 'http://pid.geoscience.gov.au/dataset/12'
# print er.x_prov_graph_pruner(g, target_entity).serialize(format='turtle')


def _prune_preconstruct(g):
    # update graph with generated/wasGeneratedBy inverse property to simplify SELECT queries
    u = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?e prov:wasGeneratedBy ?a .
        }
        WHERE {
            ?a prov:generated ?e .
        }
    '''
    g.update(u)

    # construct links between Activities to simplify SELECT queries
    u2 = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?a prov:wasInformedBy ?a2 .
        }
        WHERE {
            ?a prov:used/prov:wasGeneratedBy ?a2 .
        }
    '''
    g.update(u2)

    u3 = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?e prov:wasAttributedTo ?ag .
        }
        WHERE {
            ?e prov:wasGeneratedBy/prov:wasAssociatedWith ?ag .
        }
    '''
    g.update(u3)

    u4 = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        INSERT {
            ?e prov:wasDerivedFrom ?e_up .
        }
        WHERE {
            ?e prov:wasGeneratedBy/prov:used ?e_up .
        }
    '''
    g.update(u4)


def _get_entity_details(g, target_entity_uri):
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        CONSTRUCT {
            <%(target_entity)s> a prov:Entity .
            <%(target_entity)s> rdfs:label ?label .
            <%(target_entity)s> prov:value ?value .
            <%(target_entity)s> prov:wasGeneratedBy ?a .
            ?a2 prov:used <%(target_entity)s> .
            <%(target_entity)s> prov:wasAttributedTo ?ag .
            ?ag a prov:Agent .
            ?ag rdfs:label ?ag_label .

            <%(target_entity)s> prov:wasDerivedFrom ?e_up .
            ?e_up rdfs:label ?e_up_label .
        }
        WHERE {
            <%(target_entity)s> rdfs:label ?label .
            OPTIONAL {
                <%(target_entity)s> prov:value ?value .
            }
            OPTIONAL {
                ?a prov:generated <%(target_entity)s> .
            }
            OPTIONAL {
                ?a2 prov:used <%(target_entity)s> .
            }
            OPTIONAL {
                <%(target_entity)s> prov:wasAttributedTo ?ag .
                ?ag rdfs:label ?ag_label .
            }
            OPTIONAL {
                <%(target_entity)s> prov:wasDerivedFrom ?e_up .
                ?e_up rdfs:label ?e_up_label .
            }
        }
        ''' % {'target_entity': target_entity_uri}
    return g.query(q)


def _get_related_activity_used(g, target_entity_uri):
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        CONSTRUCT {
            # already know this from Entity details query
            # ?a prov:used <%(target_entity)s> .
            ?a a    prov:Activity .
            ?a rdfs:label ?a_label .
        }
        WHERE {
            ?a prov:used <%(target_entity)s> .
            ?a rdfs:label ?a_label .
        }
        ''' % {'target_entity': target_entity_uri}
    return g.query(q)


def _get_related_activity_generated(g, target_entity_uri):
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        CONSTRUCT {
            # already know this from Entity details query
            # <%(target_entity)s> prov:wasGeneratedBy ?a .
            ?a a    prov:Activity .
            ?a rdfs:label ?a_label .
            ?a prov:wasAssociatedWith ?ag .

            ?a prov:used ?e2 .
            ?e2 a prov:Entity ;
                rdfs:label ?e2_label .

            # inferred
            <%(target_entity)s> prov:wasAttributedTo ?ag .
        }
        WHERE {
            <%(target_entity)s> prov:wasGeneratedBy ?a .
            ?a rdfs:label ?a_label .
            OPTIONAL {
                ?a prov:used ?e2 .
                ?e2 rdfs:label ?e2_label .
            }
            OPTIONAL {
                ?a prov:wasAssociatedWith ?ag .
            }
        }
        ''' % {'target_entity': target_entity_uri}
    return g.query(q)


def _get_upstream_activity_details(g, activity_uri, target_entity):
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        CONSTRUCT {
            <%(target_activity)s> a prov:Activity ;
                rdfs:label ?label ;
                prov:used ?u .

            ?u a prov:Entity ;
                rdfs:label ?u_label .

            ?e2 prov:wasGeneratedBy <%(target_activity)s> .
        }
        WHERE {
            <%(target_activity)s> a prov:Activity ;
                rdfs:label ?label .
            OPTIONAL {
                <%(target_activity)s> prov:used ?u .
                ?u rdfs:label ?u_label .
            }
            OPTIONAL {
                ?e2 prov:wasGeneratedBy <%(target_activity)s> .
                ?a2 prov:used ?e2 .
                <%(target_entity)s> prov:wasGeneratedBy ?a2 .
            }
        }
        ''' % {
            'target_activity': activity_uri,
            'target_entity': target_entity
        }
    return g.query(q)


def _get_downstream_activity_details(g, activity_uri):
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        CONSTRUCT {
            <%(target_activity)s> a prov:Activity ;
                rdfs:label ?label .

            ?g a prov:Entity ;
                rdfs:label ?g_label ;
                prov:wasGeneratedBy <%(target_activity)s>.
        }
        WHERE {
            <%(target_activity)s> a prov:Activity ;
                rdfs:label ?label .
            OPTIONAL {
                ?g prov:wasGeneratedBy <%(target_activity)s> .
                ?g rdfs:label ?g_label .
            }
        }
        ''' % {'target_activity': activity_uri}
    return g.query(q)


def _get_upstream_activities(g, target_entity_uri):
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?a ?a2 ?ag ?ag_label
        WHERE {
            <%(target_entity)s> prov:wasGeneratedBy ?a .
            ?a prov:wasInformedBy ?a2 .
            OPTIONAL {
                ?a2 prov:wasAssociatedWith ?ag .
                ?ag rdfs:label ?ag_label .
            }
        }
        ''' % {'target_entity': target_entity_uri}

    g_upstream = Graph()
    PROV = Namespace('http://www.w3.org/ns/prov#')
    g_upstream.bind('prov', PROV)
    for r in g.query(q):
        g_upstream.add((r['a'], PROV.wasInformedBy, r['a2']))
        if r['ag'] is not None:
            g_upstream.add((r['a2'], PROV.wasAssociatedWith, r['ag']))
            g_upstream.add((r['ag'], RDF.type, PROV.Agent))
            g_upstream.add((r['ag'], RDFS.label, r['ag_label']))
        g_upstream += Graph().parse(
            data=_get_upstream_activity_details(g, str(r['a2']), target_entity_uri).serialize(format='turtle'),
            format='turtle')

    return g_upstream


def _get_downstream_activities(g, target_entity_uri):
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?a ?a2
        WHERE {
            ?a prov:used <%(target_entity)s> .
            ?a2 prov:wasInformedBy ?a .
        }
        ''' % {'target_entity': target_entity_uri}

    g_upstream = Graph()
    PROV = Namespace('http://www.w3.org/ns/prov#')
    g_upstream.bind('prov', PROV)
    for r in g.query(q):
        g_upstream.add((r['a2'], PROV.wasInformedBy, r['a']))
        g_upstream += Graph().parse(
            data=_get_downstream_activity_details(g, str(r['a2'])).serialize(format='turtle'),
            format='turtle')

    return g_upstream


def _get_upstream_entities(g, target_entity_uri):
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        CONSTRUCT {
            ?a prov:used ?e_up .
            <%(target_entity)s> prov:wasGeneratedBy ?a .

            ?e_up a prov:Entity .
            ?e_up rdfs:label ?e_up_label
        }
        WHERE {
            ?a prov:used ?e_up .
            <%(target_entity)s> prov:wasGeneratedBy ?a .
            ?e_up rdfs:label ?e_up_label
        }
        ''' % {'target_entity': target_entity_uri}
    return g.query(q)


def _get_downstream_entities(g, target_entity_uri):
    q = '''
        PREFIX prov: <http://www.w3.org/ns/prov#>
        CONSTRUCT {
            ?a prov:used <%(target_entity)s> .
            ?e_down prov:wasGeneratedBy ?a .

            ?e_down a prov:Entity .
            ?e_down rdfs:label ?e_down_label .
        }
        WHERE {
            ?a prov:used <%(target_entity)s> .
            ?e_down prov:wasGeneratedBy ?a ;
                rdfs:label ?e_down_label .
        }
        ''' % {'target_entity': target_entity_uri}
    return g.query(q)


def _get_related_agents(g, target_entity_uri):
    pass


def _get_pruned_praph(g, target_entity_uri):
    pass


def test_entity_01():
    g = Graph().parse('test_prune_01.ttl', format='turtle')
    g_static = Graph().parse('test_prune_01_result.ttl', format='turtle')

    _prune_preconstruct(g)
    target_entity_uri = 'http://test.com/entity/01'
    g_pruned = _get_entity_details(g, 'http://test.com/entity/01')

    # for r in sorted(g_static):
    #     print r
    # print '--------------------'
    # for r in sorted(g_pruned):
    #     print r

    assert rdflib.compare.isomorphic(g_pruned, g_static)


def test_entity_02():
    g = Graph().parse('test_prune_02.ttl', format='turtle')
    g_static = Graph().parse('test_prune_02_result.ttl', format='turtle')

    _prune_preconstruct(g)
    target_entity_uri = 'http://test.com/entity/01'
    # TODO: replace serialise --> deserialise graph with native SPARQLResult --> Graph conversion, if it exists
    g_pruned = Graph().parse(
        data=_get_entity_details(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_used(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_generated(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')

    # for r in sorted(g_static):
    #     print r
    # print '--------------------'
    # for r in sorted(g_pruned):
    #     print r

    assert rdflib.compare.isomorphic(g_pruned, g_static)


def test_entity_03():
    g = Graph().parse('test_prune_03.ttl', format='turtle')
    g_static = Graph().parse('test_prune_03_result.ttl', format='turtle')

    _prune_preconstruct(g)
    target_entity_uri = 'http://test.com/entity/01'
    # TODO: replace serialise --> deserialise graph with native SPARQLResult --> Graph conversion, if it exists
    # using the same functions as Test 02
    g_pruned = Graph().parse(
        data=_get_entity_details(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_used(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_generated(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')

    # for r in sorted(g_static):
    #     print r
    # print '--------------------'
    # for r in sorted(g_pruned):
    #     print r
    # exit()

    assert rdflib.compare.isomorphic(g_pruned, g_static)


def test_entity_04():
    g = Graph().parse('test_prune_04.ttl', format='turtle')
    g_static = Graph().parse('test_prune_04_result.ttl', format='turtle')

    _prune_preconstruct(g)
    target_entity_uri = 'http://test.com/entity/01'
    # TODO: replace serialise --> deserialise graph with native SPARQLResult --> Graph conversion, if it exists
    g_pruned = Graph().parse(
        data=_get_entity_details(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_used(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_generated(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_upstream_entities(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')

    # for r in sorted(g_static):
    #     print r
    # print '--------------------'
    # for r in sorted(g_pruned):
    #     print r
    # exit()

    assert rdflib.compare.isomorphic(g_pruned, g_static)


def test_entity_05():
    g = Graph().parse('test_prune_05.ttl', format='turtle')
    g_static = Graph().parse('test_prune_05_result.ttl', format='turtle')

    _prune_preconstruct(g)
    target_entity_uri = 'http://test.com/entity/01'
    # TODO: replace serialise --> deserialise graph with native SPARQLResult --> Graph conversion, if it exists
    g_pruned = Graph().parse(
        data=_get_entity_details(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_used(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_generated(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_upstream_entities(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_downstream_entities(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')

    # for r in sorted(g_static):
    #     print r
    # print '--------------------'
    # for r in sorted(g_pruned):
    #     print r

    assert rdflib.compare.isomorphic(g_pruned, g_static)


def test_entity_06():
    g = Graph().parse('test_prune_06.ttl', format='turtle')
    g_static = Graph().parse('test_prune_06_result.ttl', format='turtle')

    _prune_preconstruct(g)
    target_entity_uri = 'http://test.com/entity/01'

    # TODO: replace serialise --> deserialise graph with native SPARQLResult --> Graph conversion, if it exists
    g_pruned = Graph().parse(
        data=_get_entity_details(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_used(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_generated(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += _get_upstream_activities(g, target_entity_uri)
    g_pruned += _get_downstream_activities(g, target_entity_uri)

    # for r in sorted(g_static):
    #     print r
    # print '--------------------'
    # for r in sorted(g_pruned):
    #     print r
    # exit()

    assert rdflib.compare.isomorphic(g_pruned, g_static)


def test_entity_07():
    g = Graph().parse('test_prune_07.ttl', format='turtle')
    g_static = Graph().parse('test_prune_07_result.ttl', format='turtle')

    _prune_preconstruct(g)
    target_entity_uri = 'http://test.com/entity/01'
    # TODO: replace serialise --> deserialise graph with native SPARQLResult --> Graph conversion, if it exists
    g_pruned = Graph().parse(
        data=_get_entity_details(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_used(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_generated(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += _get_upstream_activities(g, target_entity_uri)
    g_pruned += _get_downstream_activities(g, target_entity_uri)

    # for r in sorted(g_static):
    #     print r
    # print '--------------------'
    # for r in sorted(g_pruned):
    #     print r
    # exit()

    assert rdflib.compare.isomorphic(g_pruned, g_static)


def test_entity_08():
    g = Graph().parse('test_prune_08.ttl', format='turtle')
    g_static = Graph().parse('test_prune_08_result.ttl', format='turtle')

    _prune_preconstruct(g)
    target_entity_uri = 'http://test.com/entity/01'
    # TODO: replace serialise --> deserialise graph with native SPARQLResult --> Graph conversion, if it exists
    g_pruned = Graph().parse(
        data=_get_entity_details(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_used(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_pruned += Graph().parse(
        data=_get_related_activity_generated(g, target_entity_uri).serialize(format='turtle'),
        format='turtle')
    g_up = _get_upstream_activities(g, target_entity_uri)
    print(g_up.serialize(format='turtle'))
    g_pruned += g_up
    g_pruned += _get_downstream_activities(g, target_entity_uri)

    for (s, p, o) in sorted(g_static):
        print('{:35s} {:50s} {:40s}'.format(str(s), str(p), str(o)))
    print('--------------------')
    for (s, p, o) in sorted(g_pruned):
        print('{:35s} {:50s} {:40s}'.format(str(s), str(p), str(o)))
    exit()

    assert rdflib.compare.isomorphic(g_pruned, g_static)


def test_entity_09():
    g = Graph().parse('test_prune_09.ttl', format='turtle')
    g_static = Graph().parse('test_prune_09_result.ttl', format='turtle')

    _prune_preconstruct(g)
    # TODO: replace serialise --> deserialise graph with native SPARQLResult --> Graph conversion, if it exists
    g_pruned = Graph().parse(data=_get_entity_details(g, 'http://test.com/entity/01').serialize(format='turtle'), format='turtle')
    g_pruned += Graph().parse(data=_get_related_activity_generated(g, 'http://test.com/entity/01').serialize(format='turtle'), format='turtle')

    # for r in sorted(g_static):
    #     print r
    # print '--------------------'
    # for r in sorted(g_pruned):
    #     print r

    assert rdflib.compare.isomorphic(g_pruned, g_static)


def test_entity_10():
    g = Graph().parse('test_prune_10.ttl', format='turtle')
    g_static = Graph().parse('test_prune_10_result.ttl', format='turtle')

    _prune_preconstruct(g)
    # TODO: replace serialise --> deserialise graph with native SPARQLResult --> Graph conversion, if it exists
    g_pruned = Graph().parse(data=_get_entity_details(g, 'http://test.com/entity/01').serialize(format='turtle'), format='turtle')
    g_pruned += Graph().parse(data=_get_related_activity_generated(g, 'http://test.com/entity/01').serialize(format='turtle'), format='turtle')

    # for r in sorted(g_static):
    #     print r
    # print '--------------------'
    # for r in sorted(g_pruned):
    #     print r

    assert rdflib.compare.isomorphic(g_pruned, g_static)


if __name__ == '__main__':
    # print 'Test 01'
    # test_entity_01()
    # print 'Test 02'
    # test_entity_02()
    # print 'Test 03'
    # test_entity_03()
    # print 'Test 04'
    # test_entity_04()
    # print 'Test 05'
    # test_entity_05()
    # print 'Test 06'
    # test_entity_06()
    # print 'Test 07'
    # test_entity_07()
    print('Test 08')
    test_entity_08()
    # print 'Test 09'
    # test_entity_09()
    # print 'Test 10'
    # test_entity_10()
