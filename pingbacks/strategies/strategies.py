import datetime
import settings
from pingbacks.strategies import strategy_functions
from pingbacks.status_recorder import sr_functions

strategies = [
    {'id': 0, 'title': 'No Action'},
    {'id': 1, 'title': 'Given Pingback'},
    {'id': 2, 'title': 'Given Provenance'},
    {'id': 3, 'title': 'Known Provenance Stores'},
    {'id': 4, 'title': 'Pingback Lookup'},
    {'id': 5, 'title': 'Provenance Lookup'}
]


def do_pingbacks(entities, entity_status_store, strategies):
    total_count = 0
    for entity_uri in entities:
        total_count += 1
        do_pingback(entity_uri, entity_status_store, settings.STRATEGIES)

    return total_count


# TODO: complete
def do_pingback(entity_uri, entity_status_store, strategies):
    possible_strategies = strategies
    sr_functions.update_entity_status(entity_status_store, entity_uri, {'last_attempt': datetime.datetime.now().isoformat()})

    # check Entity to see if is dereferencable
    is_dereferencable_var = strategy_functions.is_dereferencable(entity_uri)
    if is_dereferencable_var[0]:
        sr_functions.update_entity_status(entity_status_store, entity_uri, {'dereferencable': True})

        # if Entity is dereferencable, check to see if it has RDF
        has_rdf_meatadata_var = strategy_functions.has_valid_rdf_meatadata(is_dereferencable_var[1], is_dereferencable_var[2]['Content-Type'])
        if has_rdf_meatadata_var[0]:
            sr_functions.update_entity_status(entity_status_store, entity_uri, {'rdf_metadata': True})
        else:
            # if no RDF metadata, some strategies are impossible
            if 5 in possible_strategies:
                possible_strategies.remove(4)
            if 6 in possible_strategies:
                possible_strategies.remove(5)
    else:
        # if not dereferencable, some strategies are impossible
        if 5 in possible_strategies:
            possible_strategies.remove(4)
        if 6 in possible_strategies:
            possible_strategies.remove(5)

    # choose pingback actions based on selected Strategies
    for strategy in strategies:
        if strategy == 0:
            pingback_endpoints_var = strategy_functions.get_pingback_endpoints_via_given(has_rdf_meatadata_var[1], entity_uri)
            if pingback_endpoints_var[0]:
                sr_functions.update_entity_status(entity_status_store, entity_uri, {'pingback_endpoints': pingback_endpoints_var[1]})

            print pingback_endpoints_var
        if strategy == 1:
            has_provenance_endpoints_var = strategy_functions.get_provenance_query_service_endpoints_via_given(has_rdf_meatadata_var[1], entity_uri)
        if strategy == 2:
            # do actions for Strategy 2
            pass
        if strategy == 3:
            # do actions for Strategy 3
            pass
        if strategy == 4:
            has_pingback_endpoints_var = strategy_functions.get_pingback_endpoints_via_lookup(has_rdf_meatadata_var[1], entity_uri)
        if strategy == 5:
            has_pingback_endpoints_var = strategy_functions.has_provenance_query_service_endpoints_via_lookup(has_rdf_meatadata_var[1], entity_uri)
