from modules.pingbacks.engine import Engine
from rdflib import Graph
import os
import _config as conf


def test_entity_selection():
    g = Graph().parse(
        source=os.path.join(__init__.APP_DIR, 'modules', 'pingbacks', '_tests', 'test_proms_report_internal.ttl'),
        format='turtle'
    )

    e = Engine(g, 'http://example.com/report', 'http://fake-instance-endpoint.com', 'http://fake-sparql-endpoint.com')

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

    actual_results = e.get_candidates()

    assert set(expected_results) == set(actual_results)


def test_get_strategies_enabled():
    e = Engine(Graph(), 'nothing')
    strategies = e.get_strategies_enabled()

    assert len(strategies) == 1  # by default, none only enabled strategy


def test_all():
    g = Graph().parse(
        source=os.path.join(__init__.APP_DIR, 'modules', 'pingbacks', '_tests', 'test_proms_report_internal.ttl'),
        format='turtle'
    )

    e = Engine(g, 'http://example.com/report', 'http://localhost:9000/instance', 'http://fake-sparql-endpoint.com')

if __name__ == "__main__":
    # test_entity_selection()
    # test_get_strategies_enabled()
    test_all()
    # from modules.pingbacks.status_recorder import StatusRecorder
    # sr = StatusRecorder()
    # sr.clear()


