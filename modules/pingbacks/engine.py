import os
import json
from datetime import datetime
from .status_recorder import StatusRecorder
import strategy_functions
import generator


class Engine:
    def __init__(self, graph, report_uri, instance_endpoint, sparql_endpoint):
        """Starts the whole Pingbacks lifecycle."""
        self.graph = graph
        self.report_uri = report_uri
        self.instance_endpoint = instance_endpoint
        self.sparql_endpoint = sparql_endpoint

        # find pingback candidates
        self.candidates = self.get_candidates()

        # store them
        self.status_recorder = StatusRecorder()
        self.add_candidates_to_status_store()

        # finds out the Pingbacks strategies applied in this instance
        self.strategies = self.get_strategies_enabled()

        # attempt pingbacks per candidate, using enabled strategies
        self.do_pingbacks()

    def get_candidates(self):
        """Gets all the candidate URIs for which to send Pingbacks

        Follows the criteria outlined at http://promsns.org/
        """
        # TODO: remove Plan union and subClassOf statements after inferencing added to provenance DB
        q = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX proms: <http://promsns.org/def/proms#>
            SELECT ?e ?el
            WHERE {
                # Criteria 1 - inferencing
                # ?c rdfs:subClassOf* prov:Entity .
                # {?e rdf:type ?c .}

                {?e a prov:Entity .}
                UNION
                {?e a proms:ServiceEntity .}
                UNION
                {?e a prov:Plan .}

                OPTIONAL {
                    ?e  rdfs:label  ?el .
                }

                # Criteria 2
                MINUS {?a  prov:generated ?e .}
                # Criteria 2
                MINUS {?e prov:wasGeneratedBy ?a .}
                # Criteria 3
                MINUS {?e prov:wasDerivedFrom ?e2 .}
                # Criteria 4
                # no externally-defined Entities can use the ENTITY_BASE_URI of the PROMS Server
                FILTER regex(STR(?e), "^((?!%(report_uri)s).)*$", "i")
            }
            ORDER BY ASC(?el)
        ''' % {'report_uri': self.report_uri}
        candidates = []
        for triple in self.graph.query(q):
            candidates.append(str(triple['e']))

        return candidates

    def add_candidates_to_status_store(self):
        for candidate in self.candidates:
            self.status_recorder.add(candidate)

    # def dereference_entity(entity_uri):
    #     r = requests.get(entity_uri, allow_redirects=True)
    #     if r.status_code == 200:
    #         return True
    #     else:
    #         return False
    #
    #
    # def get_entity_rdf(entity_uri):
    #     r = requests.get(entity_uri,
    #                      allow_redirects=True,
    #                      headers={'Accept': 'text/turtle, application/rdf+xml, application/ld+json'})
    #     if r.status_code == 200:
    #         return [True, r.text]
    #     else:
    #         return [False, r.text]
    #
    #
    # def get_entities_for_pingbacks2(g):
    #     q = '''
    #         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    #         PREFIX prov: <http://www.w3.org/ns/prov#>
    #         PREFIX proms: <http://promsns.org/def/proms#>
    #         SELECT ?e ?el ?b
    #         WHERE {
    #             # Criteria 1 - inferencing
    #             #?c rdfs:subClassOf* prov:Entity .
    #             #?e rdf:type ?c .
    #
    #             # Criteria 1 - static
    #             { ?e a prov:Entity . }
    #             UNION
    #             { ?e a prov:Collection . }
    #             UNION
    #             { ?e a prov:Plan . }
    #             UNION
    #             { ?e a <http://promsns.org/def/proms#ServiceEntity> . }
    #
    #             ?e  rdfs:label  ?el .
    #
    #             # Criteria 2
    #             MINUS {?a  prov:generated ?e .}
    #             MINUS {?e prov:wasGeneratedBy ?a .}
    #
    #             # Criteria 3
    #             MINUS {?e prov:wasDerivedFrom ?e2 .}
    #             MINUS {?e prov:wasRevisionOf ?e2 .}  # could be others
    #
    #             # Criteria 4
    #             {
    #                 SELECT ?b
    #                 WHERE {
    #                     {?r a proms:ExternalReport .}
    #                     UNION
    #                     {?r a proms:InternalReport .}
    #                     BIND(STRBEFORE(STR(?r), "#" ) AS ?b)
    #                 }
    #             }
    #             FILTER regex(STR(?e), CONCAT("^((?!", ?b, ").)*$"), "i")
    #         }
    #         ORDER BY ASC(?el)
    #     '''
    #     actual_results = []
    #     for triple in g.query(q):
    #         actual_results.append(str(triple['e']))
    #
    #     return actual_results

    def get_strategies_enabled(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        strategies = json.load(open(os.path.join(dir_path, 'strategies-config.json')))

        return list({str(k) for k, v in strategies.iteritems() if v['enabled']})

    def do_pingbacks(self):
        total_count = 0
        for candidate in self.candidates:
            total_count += 1
            self._do_pingback(candidate)

        return total_count

    def _do_pingback(self, candidate):
        # update the status store to record the time of this attempts for this entity
        self.status_recorder.update(candidate, {'last_attempt': datetime.now().isoformat()})

        # get stored details
        candidate_status = strategy_functions.is_dereferencable(candidate)

        # try each enabled strategy for this candidate
        for strategy in self.strategies:
            eval('self._try_strategy_' + strategy + '("' + candidate + '")')

        # # try pingback using stored details
        #
        #
        # # check Entity to see if is dereferencable
        # if not self.status_recorder.load(candidate).get('dereferencable'):
        #     is_dereferencable =
        #
        # if is_dereferencable[0]:
        #     self.status_recorder.update(candidate, {'dereferencable': True})
        #
        #     # if Entity is dereferencable, check to see if it has RDF
        #     has_rdf_meatadata_var = strategy_functions.has_valid_rdf_meatadata(is_dereferencable[1], is_dereferencable[2]['Content-Type'])
        #     if has_rdf_meatadata_var[0]:
        #         self.status_recorder.update(candidate, {'rdf_metadata': True})
        #     else:
        #         # if no RDF metadata, some strategies are impossible
        #         if 5 in possible_strategies:
        #             possible_strategies.remove(4)
        #         if 6 in possible_strategies:
        #             possible_strategies.remove(5)
        # else:
        #     # if not dereferencable, some strategies are impossible
        #     if 5 in possible_strategies:
        #         possible_strategies.remove(4)
        #     if 6 in possible_strategies:
        #         possible_strategies.remove(5)
        #
        # # choose pingback actions based on selected Strategies
        # for strategy in self.strategies:
        #     if strategy == 0:
        #         pingback_endpoints_var = strategy_functions.get_pingback_endpoints_via_given(has_rdf_meatadata_var[1], candidate)
        #         if pingback_endpoints_var[0]:
        #             status_recorder.update(entity_status_store, candidate, {'pingback_endpoints': pingback_endpoints_var[1]})
        #
        #         print pingback_endpoints_var
        #     if strategy == 1:
        #         has_provenance_endpoints_var = strategy_functions.get_provenance_query_service_endpoints_via_given(has_rdf_meatadata_var[1], candidate)
        #     if strategy == 2:
        #         # do actions for Strategy 2
        #         pass
        #     if strategy == 3:
        #         # do actions for Strategy 3
        #         pass
        #     if strategy == 4:
        #         has_pingback_endpoints_var = strategy_functions.get_pingback_endpoints_via_lookup(has_rdf_meatadata_var[1], candidate)
        #     if strategy == 5:
        #         has_pingback_endpoints_var = strategy_functions.has_provenance_query_service_endpoints_via_lookup(has_rdf_meatadata_var[1], candidate)

    def _try_strategy_given_endpoint(self, candidate):
        # get the prov:pingback property
        query = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE {
                ?s ?p ?o .
                <%s> prov:pingback ?o .
            }
        ''' % candidate
        pingback_endpoint = None
        for row in self.graph.query(query):
            pingback_endpoint = row['o']

        if pingback_endpoint is not None:
            # send both types of Pingback message
            paq = generator.ProvAqPingback(candidate, self.instance_endpoint, self.sparql_endpoint)
            paq.send_dummy(pingback_endpoint)
            proms = generator.PromsPingback(candidate, self.instance_endpoint)
            proms.send_dummy(pingback_endpoint)

    def _try_strategy_given_provenance(self, candidate):
        print('trying _try_strategy_given_provenance')

    def _try_strategy_known_stores(self, candidate):
        print('trying _try_strategy_known_stores')

    def _try_strategy_pingback_lookup(self, candidate):
        print('trying _try_strategy_pingback_lookup')

    def _try_strategy_provenance_lookup(self, candidate):
        print('trying _try_strategy_provenance_lookup')
