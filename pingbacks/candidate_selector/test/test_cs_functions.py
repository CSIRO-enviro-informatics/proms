from pingbacks.candidate_selector import cs_functions
from rdflib import Graph


def test_get_report_uri_base():
    g = Graph().parse(source='test_proms_report_internal.ttl', format='turtle')
    expected_result = 'http://example.com/report#'
    actual_result = cs_functions.get_report_uri_base(g)
    return expected_result == actual_result


def test_entity_selection():
    g = Graph().parse(source='test_proms_report_internal.ttl', format='turtle')

    expected_results = [
        'http://example.com/default#e_a',
        'http://example.com/default#e_b',
        'http://example.com/default#e_c',
        'http://example.com/default#e_d',
        'http://example.com/default#e_h',
        'http://example.com/default#e_k',
        'http://example.com/default#e_l',
        'http://example.com/default#e_p',
        'http://example.com/default#e_s'
    ]

    actual_results = cs_functions.get_entities_for_pingbacks(g)

    return set(expected_results) == set(actual_results)


if __name__ == "__main__":
    print test_get_report_uri_base()
    print test_entity_selection()

    '''
    # test the Report used for strategy testing
    g = Graph().parse(source='../../strategies/test/test-proms-report-external.ttl', format='turtle')
    import pprint
    pprint.pprint(cs_functions.get_entities_for_pingbacks(g))
    '''