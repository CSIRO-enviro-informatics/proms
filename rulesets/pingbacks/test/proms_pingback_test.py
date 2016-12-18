from rulesets.pingbacks import PromsPingback
from requests import request


def test_proms_rs_pass():
    request.headers = {
        'Content-Type': 'text/turtle'
    }
    pingback_endpoint = 'http://localhost/api/pingback'
    request.content = open('proms_pingback_valid.ttl', 'r').read().replace('{PB}', pingback_endpoint)

    p = PromsPingback(request, pingback_endpoint)

    assert p.passed


def test_proms_rs_fail():
    request.headers = {
        'Content-Type': 'text/turtle'
    }
    pingback_endpoint = 'http://localhost/api/pingback'
    request.content = open('proms_pingback_invalid.ttl', 'r').read().replace('{PB}', pingback_endpoint)

    p = PromsPingback(request, pingback_endpoint)

    assert not p.passed


def test_proms_rs_fail2():
    request.headers = {
        'Content-Type': 'text/turtle'
    }
    pingback_endpoint = 'http://localhost/api/pingback'
    request.content = open('proms_pingback_invalid2.ttl', 'r').read().replace('{PB}', pingback_endpoint)

    p = PromsPingback(request, pingback_endpoint)

    assert not p.passed


if __name__ == '__main__':
    # test_proms_rs_pass()
    test_proms_rs_fail()
    # test_proms_rs_fail2()
