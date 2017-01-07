import requests


def test_lodge_prov_pingback_01():
    r = requests.post(
        'http://localhost:9000/function/lodge_pingback',
        data='http://fred.com\nhttps://freds.com',
        headers={'Content-Type': 'text/uri-list'}
    )

    assert r.status_code == 204


def test_lodge_prov_pingback_02():
    r = requests.post(
        'http://localhost:9000/function/lodge_pingback',
        data='http://fred.com\nhttps://freds.com\nhtp://broken.com',
        headers={'Content-Type': 'text/uri-list'}
    )

    assert r.status_code == 400


def test_lodge_proms_pingback_01():
    pingback_endpoint = 'http://localhost:9000/function/lodge_pingback'
    ttl_data = open('../../modules/rulesets/pingbacks/tests/proms_pingback_valid.ttl', 'rb').read().replace(
        '{PB}', pingback_endpoint)

    #print ttl_data
    # from rdflib import Graph
    # g = Graph().parse(data=ttl_data, format='turtle')
    #
    # q = '''
    #         PREFIX prov: <http://www.w3.org/ns/prov#>
    #         ASK
    #         WHERE {
    #             {?e  a prov:Entity .}
    #             ?e    prov:pingback <%s> .
    #         }
    #     ''' % pingback_endpoint
    #
    # for r in g.query(q):
    #     print r

    r = requests.post(
        pingback_endpoint,
        data=ttl_data,
        headers={'Content-Type': 'text/turtle'}
    )

    assert r.status_code == 204


def test_lodge_proms_pingback_02():
    pingback_endpoint = 'http://localhost:9000/function/lodge_pingback'
    ttl_data = open('../../modules/rulesets/pingbacks/tests/proms_pingback_invalid.ttl', 'rb').read().replace(
        '{PB}', pingback_endpoint)

    r = requests.post(
        pingback_endpoint,
        data=ttl_data,
        headers={'Content-Type': 'text/turtle'}
    )

    assert r.status_code != 204


def test_lodge_proms_pingback_03():
    pingback_endpoint = 'http://localhost:9000/function/lodge_pingback'
    ttl_data = open('../../modules/rulesets/pingbacks/tests/proms_pingback_invalid2.ttl', 'rb').read().replace(
        '{PB}', pingback_endpoint)

    r = requests.post(
        pingback_endpoint,
        data=ttl_data,
        headers={'Content-Type': 'text/turtle'}
    )

    print r.content
    assert r.status_code != 204


if __name__ == '__main__':
    # test_lodge_prov_pingback_01()
    # test_lodge_prov_pingback_02()
    test_lodge_proms_pingback_01()
    # test_lodge_proms_pingback_02()
    # test_lodge_proms_pingback_03()
