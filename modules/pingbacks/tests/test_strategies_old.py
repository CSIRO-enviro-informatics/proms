# import logging
# import imp
# util = imp.load_source('strategy_functions', '../strategy_functions.py')
# from modules.pingbacks.strategies import strategy_functions
#
#
# def get_entities(g):
#     q = '''
#     PREFIX prov: <http://www.w3.org/ns/prov#>
#     SELECT ?e
#     WHERE {
#         ?e a prov:Entity .
#     }
#     '''
#
#     entity_uris = []
#     for row in g.query(q):
#         entity_uris.append(str(row['e']))
#
#     return entity_uris
#
#
# def make_test_report():
#     return '''
#
#
#     '''
#
#
# def test_strategy_1(ttl_file_path):
#     expected_results = [
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/99',
#             'pingback_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/1',
#             'pingback_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/2',
#             'pingback_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/3',
#             'pingback_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/4',
#             'pingback_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/5',
#             'pingback_endpoints': ['http://proms-dev1-vc.it.csiro.au/function/pingback/']
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/6',
#             'pingback_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/7',
#             'pingback_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/8',
#             'pingback_endpoints': ['http://example.com/api/pingback', 'http://example.com/function/pingback/']
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/9',
#             'pingback_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/10',
#             'pingback_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/11',
#             'pingback_endpoints': []
#         }
#     ]
#     expected_results = sorted(expected_results, key=lambda k: k['entity_uri'])
#
#     g = strategy_functions.get_graph(ttl_file_path)
#
#     entity_uris = get_entities(g)
#     actual_results = []
#     for entity_uri in entity_uris:
#         actual_results.append(
#             {
#                 'entity_uri': entity_uri,
#                 'pingback_endpoints': strategy_functions.get_pingback_endpoints_via_given(g, entity_uri)
#             }
#         )
#
#     if len(actual_results) != len(expected_results):
#         return [False, 'incorrect number of entities, expected ' + str(len(expected_results)) + ', got ' + str(len(actual_results))]
#
#     actual_results = sorted(actual_results, key=lambda k: k['entity_uri'])
#
#     i = 0
#     passes = True
#     reasons = []
#     for entity in actual_results:
#         entity['pingback_endpoints'].sort()
#         expected_results[i]['pingback_endpoints'].sort()
#
#         if entity['pingback_endpoints'] != expected_results[i]['pingback_endpoints']:
#             passes = False
#             reasons.append('incorrect result for ' + entity['entity_uri'])
#         i += 1
#
#     if passes:
#         return [True]
#     else:
#         return [False, reasons]
#
#
# def test_strategy_2(ttl_file_path):
#     expected_results = [
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/99',
#             'provenance_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/1',
#             'provenance_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/2',
#             'provenance_endpoints': ['http://example.com/function/sparql']
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/3',
#             'provenance_endpoints': ['http://example.com', 'http://example2.com']
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/4',
#             'provenance_endpoints': ['http://example.com/api/sparql']
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/5',
#             'provenance_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/6',
#             'provenance_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/7',
#             'provenance_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/8',
#             'provenance_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/9',
#             'provenance_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/10',
#             'provenance_endpoints': []
#         },
#         {
#             'entity_uri': 'http://promsns.org/datastoredemo/id/dataset/11',
#             'provenance_endpoints': []
#         }
#     ]
#     expected_results = sorted(expected_results, key=lambda k: k['entity_uri'])
#
#     g = strategy_functions.get_graph(ttl_file_path)
#
#     entity_uris = get_entities(g)
#     actual_results = []
#     for entity_uri in entity_uris:
#         actual_results.append(
#             {
#                 'entity_uri': entity_uri,
#                 'provenance_endpoints': strategy_functions.get_provenance_query_service_endpoints_via_given(g, entity_uri)
#             }
#         )
#
#     if len(actual_results) != len(expected_results):
#         return [False, 'incorrect number of entities, expected ' + str(len(expected_results)) + ', got ' + str(len(actual_results))]
#
#     actual_results = sorted(actual_results, key=lambda k: k['entity_uri'])
#
#     i = 0
#     passes = True
#     reasons = []
#     for entity in actual_results:
#         entity['provenance_endpoints'].sort()
#         expected_results[i]['provenance_endpoints'].sort()
#
#         if entity['provenance_endpoints'] != expected_results[i]['provenance_endpoints']:
#             passes = False
#             reasons.append('incorrect result for ' + entity['entity_uri'])
#         i += 1
#
#     if passes:
#         return [True]
#     else:
#         return [False, reasons]
#
#
# if __name__ == "__main__":
#     logging.basicConfig()
#     '''
#     TEST_ENTITY_STATUS_STORE = settings.HOME_DIR + 'strategies/test/test_entity_state_store.json'
#     TEST_ENTITIES = [
#         'http://broken_link.com/resource/1',
#         'http://promsns.org/',
#         'http://broken_link.com/resource/2',
#         'http://broken_link.com/resource/4',
#         'http://promsns.org/eg/entity-server/id/dataset/001',
#         'http://promsns.org/eg/entity-server/id/dataset/002',
#         'http://promsns.org/eg/entity-server/id/dataset/003',
#         'http://promsns.org/eg/entity-server/id/dataset/004',
#         'http://promsns.org/eg/entity-server/id/dataset/005',
#         'http://promsns.org/eg/entity-server/id/dataset/006'
#     ]
#     count = strategies.do_pingbacks(TEST_ENTITIES, TEST_ENTITY_STATUS_STORE, [1])
#     '''
#     print "hello"