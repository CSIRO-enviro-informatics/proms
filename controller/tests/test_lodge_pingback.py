import requests


def test_lodge_prov_pingback_01():
    """Valid"""
    r = requests.post(
        'http://localhost:9000/function/lodge-pingback?resource_uri=http%3A%2F%2Fthing.com%2F1',
        data='http://fred.com\nhttps://freds.com',
        headers={'Content-Type': 'text/uri-list'}
    )

    assert r.status_code == 204


def test_lodge_prov_pingback_02():
    """Invalid - resource_uri is not a valid URI"""
    r = requests.post(
        'http://localhost:9000/function/lodge-pingback?resource_uri=htp%3A%2F%2Fthing.com%2F1',
        data='http://fred.com\nhttps://freds.com',
        headers={'Content-Type': 'text/uri-list'}
    )

    assert r.status_code == 400


def test_lodge_prov_pingback_03():
    """Invalid - malformed URI in body"""
    r = requests.post(
        'http://localhost:9000/function/lodge-pingback?resource_uri=http%3A%2F%2Fthing.com%2F1',
        data='http://fred.com\nhttps://freds.com\nhtp://broken.com',
        headers={'Content-Type': 'text/uri-list'}
    )
    assert r.status_code == 400


def test_lodge_prov_pingback_04():
    """Invalid - no resource_uri query string argument"""
    r = requests.post(
        'http://localhost:9000/function/lodge-pingback',
        data='http://fred.com',
        headers={'Content-Type': 'text/uri-list'}
    )
    assert r.status_code == 400


def test_lodge_prov_pingback_05():
    """Valid - with link headers"""
    r = requests.post(
        'http://localhost:9000/function/lodge-pingback?resource_uri=http%3A%2F%2Fthing.com%2F1',
        data='http://fred.com',
        headers={
            'Content-Type': 'text/uri-list',
            'Link': '<http://example.com/sparql>; rel="http://www.w3.org/ns/prov#has_query_service"; anchor="http://example.com/x/y/z",<http://example.com/something.rdf>; rel="http://www.w3.org/ns/prov#has_provenance"; anchor="http://example.com/p/q/r"'
        }
    )
    assert r.status_code == 204


def test_lodge_prov_pingback_06():
    """Invalid - bad link headers, 1st has no < or > around URI"""
    r = requests.post(
        'http://localhost:9000/function/lodge-pingback?resource_uri=http%3A%2F%2Fthing.com%2F1',
        data='http://fred.com',
        headers={
            'Content-Type': 'text/uri-list',
            'Link': 'http://example.com/sparql; rel="http://www.w3.org/ns/prov#has_query_service"; anchor="http://example.com/x/y/z",<http://example.com/something.rdf>; rel="http://www.w3.org/ns/prov#has_provenance"; anchor="http://example.com/p/q/r"'
        }
    )
    assert r.status_code == 400


def test_lodge_proms_pingback_01():
    pingback_endpoint = 'http://localhost:9000/function/lodge-pingback'
    ttl_data = open('../../modules/rulesets/pingbacks/_tests/proms_pingback_valid.ttl', 'rb').read().replace(
        '{PB}', pingback_endpoint)

    r = requests.post(
        pingback_endpoint,
        data=ttl_data,
        headers={'Content-Type': 'text/turtle'}
    )

    assert r.status_code == 204


def test_lodge_proms_pingback_02():
    pingback_endpoint = 'http://localhost:9000/function/lodge-pingback'
    ttl_data = open('../../modules/rulesets/pingbacks/_tests/proms_pingback_invalid.ttl', 'rb').read().replace(
        '{PB}', pingback_endpoint)

    r = requests.post(
        pingback_endpoint,
        data=ttl_data,
        headers={'Content-Type': 'text/turtle'}
    )

    assert r.status_code != 204


def test_lodge_proms_pingback_03():
    pingback_endpoint = 'http://localhost:9000/function/lodge-pingback'
    ttl_data = open('../../modules/rulesets/pingbacks/_tests/proms_pingback_invalid2.ttl', 'rb').read().replace(
        '{PB}', pingback_endpoint)

    r = requests.post(
        pingback_endpoint,
        data=ttl_data,
        headers={'Content-Type': 'text/turtle'}
    )

    print(r.content)
    assert r.status_code != 204


if __name__ == '__main__':
    # test_lodge_prov_pingback_01()
    # test_lodge_prov_pingback_02()
    # test_lodge_prov_pingback_03()
    # test_lodge_prov_pingback_04()
    # test_lodge_prov_pingback_05()
    # test_lodge_prov_pingback_06()
    test_lodge_proms_pingback_01()
    # test_lodge_proms_pingback_02()
    # test_lodge_proms_pingback_03()
