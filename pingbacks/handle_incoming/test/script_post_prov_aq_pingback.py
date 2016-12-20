import requests
import settings


def post_static_prov_aq_pingback():
    headers = {}
    headers['Content-Type'] = 'text/uri-list'
    headers['Content-Length'] = '0'
    link_header1 = '<http://entity.com/1>; ' + \
                  'rel="http://www.w3.org/ns/prov#has_provenance; ' + \
                  'anchor="http://somewhere-else.com"'
    link_header2 = '<http://entity.com/1>; ' + \
                  'rel="http://www.w3.org/ns/prov#has_provenance; ' + \
                  'anchor="http://somewhere-else-else.com"'
    headers['Link'] = link_header1 + ', ' + link_header2

    send_to = settings.BASE_URI + '/function/pingback'
    print send_to
    r = requests.post(send_to,
                      data=None,
                      headers=headers)


    print r.status_code
    print r.content