from modules.ldapi.ldapi import LDAPI


def test_get_rdf_mimetypes_list():
    l1 = set(LDAPI.get_rdf_mimetypes_list())
    l2 = {
        'application/rdf+xml',
        'text/turtle',
        'application/rdf+json',
        'application/json',
        'text/ntriples',
        'text/n3',
        'text/nt'
    }
    assert l1 == l2


def test_get_rdf_parser_for_mimetype():
    assert LDAPI.get_rdf_parser_for_mimetype('application/rdf+xml') == 'xml'


def test_get_mimetype_for_rdf_parser():
    assert LDAPI.get_mimetype_for_rdf_parser('turtle') == 'text/turtle'


if __name__ == '__main__':
    #test_get_mimetype_for_rdf_parser()
    #test_get_rdf_parser_for_mimetype()
    test_get_rdf_mimetypes_list()
