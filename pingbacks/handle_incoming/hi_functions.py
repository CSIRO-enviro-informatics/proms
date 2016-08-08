def is_provaq_msg(request):
    # the only test for a PROV-AQ message is currently whether or not its Content Type is == text/uri-list
    if request.headers['Content-Type'] == 'text/uri-list':
        return True


def register_provaq_pingback(request):
    # PROMS ignores URIs in the message body since it doesn't know which Entity they are for
    # check to see if there are Link headers
    if request.headers.get('Link'):
        print request.headers.get('Link')
    return True


def is_proms_msg(request):
    # the only test for a PROMS message is currently whether or not its Content Type is one of the known RDF mimetypes
    # TODO: include all RDF content types
    rdf_mimetype = [
        'text/turtle',
        'text/n3',
        'application/rdf+json'
        'application/rdf+xml'
    ]
    if request.headers['Content-Type'] in rdf_mimetype:
        return True


def register_proms_pingback(request):
    return True