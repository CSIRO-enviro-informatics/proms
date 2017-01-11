import datetime
import json
from modules.pingbacks.status_recorder import StatusRecorder


def test_add():
    """Tests adding and entity only"""
    # reset the test store to empty
    sr = StatusRecorder()
    sr.clear()

    sr.add('http://test.com/entity/42')
    sr.add('http://test.com/entity/43')
    sr.add('http://test.com/entity/44')

    expected_results = [
        'http://test.com/entity/42',
        'http://test.com/entity/43',
        'http://test.com/entity/44'
    ]

    actual_results = []
    with open(sr.status_recorder.get('status_store'), 'r') as f:
        entities = json.load(f)
    for entity in entities:
        actual_results.append(entity.get('uri'))

    assert set(expected_results) == set(actual_results)


def test_add_load_update():
    """Tests adding, loading and updating an entity"""
    sr = StatusRecorder()
    sr.clear()
    test_uri = 'http://test.com/entity/42'
    test_time = datetime.datetime.now().isoformat()
    test_entity = {
        'uri': test_uri,
        'strategies': [0],
        'first_attempt': test_time,
        'last_attempt': test_time,
        'dereferencable': True,
        'rdf_metadata': False,
        'pingback_endpoints': None,
        'provenance_endpoints': None,
        'pingback_received': False,
        'provenance_bundle_received': False
    }
    sr.add(test_uri)

    sr.update(test_uri, {
        'last_attempt': test_time,
        'dereferencable': True
    })

    loaded_entity = sr.load(test_uri)

    assert loaded_entity == test_entity
    # # create a new Entity in the entity state store
    # sr_functions.create_entity_status(TEST_ENTITY_STATUS_STORE, 'http://test.com/dataset/1')
    #
    # # set the static comparison
    # expected_entity_status = {
    #     'uri': 'http://test.com/dataset/1',
    #     'strategies': [0],
    #     #'first_attempt': datetime.datetime.now().isoformat(), -- cannot use in comparison since set at run time
    #     'last_attempt': None,
    #     'dereferencable': False,
    #     'rdf_metadata': False,
    #     'pingback_endpoints': None,
    #     'provenance_endpoints': None,
    #     'pingback_received': False,
    #     'provenance_bundle_received': False
    # }
    #
    # # get the created entity back
    # with open(TEST_ENTITY_STATUS_STORE, 'r') as f:
    #     entity_statuses = json.load(f)
    #
    # for entity_status in entity_statuses:
    #     if entity_status['uri'] == 'http://test.com/dataset/1':
    #         actual_entity_status = entity_status
    #
    # # remove the first attempt as cannot use in comparison since set at run time
    # del actual_entity_status['first_attempt']
    #
    # # compare
    # return expected_entity_status == actual_entity_status


def test_update_entity_status():
    # reset the test store to empty
    sr_functions.clear_entity_state_store(TEST_ENTITY_STATUS_STORE)

    # create two entity_statuses
    e1 = {
        'uri': 'http://test.com/dataset/1',
        'strategies': [0],
        'first_attempt': datetime.datetime.now().isoformat(),
        'last_attempt': None,
        'dereferencable': False,
        'rdf_metadata': False,
        'pingback_endpoints': None,
        'provenance_endpoints': None,
        'pingback_received': False,
        'provenance_bundle_received': False
    }
    e2 = {
        'uri': 'http://test.com/dataset/2',
        'strategies': [1, 2, 3],
        'first_attempt': datetime.datetime.now().isoformat(),
        'last_attempt': None,
        'dereferencable': True,
        'rdf_metadata': True,
        'pingback_endpoints': 'http://test.com/api/pingback',
        'provenance_endpoints': None,
        'pingback_received': False,
        'provenance_bundle_received': False
    }
    entity_statuses = [e1, e2]

    # save to test store
    with open(TEST_ENTITY_STATUS_STORE, 'w') as f:
        f.write(json.dumps(entity_statuses, indent=4, sort_keys=True))

    # alter the expected entity_status
    e2['provenance_endpoints'] = ['http://test.com/api/pingback', 'http://test.com/api/pingback2']
    e2['pingback_received'] = True

    # try to update an stored entity_status
    updated_fields = {
        'provenance_endpoints': ['http://test.com/api/pingback', 'http://test.com/api/pingback2'],
        'pingback_received': True,
    }
    sr_functions.update_entity_status(TEST_ENTITY_STATUS_STORE, 'http://test.com/dataset/2', updated_fields)

    # load the updated entity_status
    e = sr_functions.load_entity_status(TEST_ENTITY_STATUS_STORE, 'http://test.com/dataset/2')

    # compare
    return e == e2


if __name__ == "__main__":
    test_add()
    test_add_load_update()

