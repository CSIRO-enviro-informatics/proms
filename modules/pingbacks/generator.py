import requests
import urllib.parse as uriparse


#
#   generic pingback message functions
#
def is_a_uri(uri_candidate):
    """
    Validates a string as a URI

    :param uri_candidate: string
    :return: True or False
    """
    import re
    # https://gist.github.com/dperini/729294
    URL_REGEX = re.compile(
        u"^"
        # protocol identifier
        u"(?:(?:https?|ftp)://)"
        # user:pass authentication
        u"(?:\S+(?::\S*)?@)?"
        u"(?:"
        # IP address exclusion
        # private & local networks
        u"(?!(?:10|127)(?:\.\d{1,3}){3})"
        u"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
        u"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
        # IP address dotted notation octets
        # excludes loopback network 0.0.0.0
        # excludes reserved space >= 224.0.0.0
        # excludes network & broadcast addresses
        # (first & last IP address of each class)
        u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
        u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
        u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
        u"|"
        # host name
        u"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
        # domain name
        u"(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
        # TLD identifier
        u"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
        u")"
        # port number
        u"(?::\d{2,5})?"
        # resource path
        u"(?:/\S*)?"
        u"$"
        , re.UNICODE
    )
    return re.match(URL_REGEX, uri_candidate)


def serialize_http_message(headers, body):
    msg = ''
    for k, v in sorted(headers.items()):
        msg += k + ': ' + str(v) + '\n'
    if body:
        msg += '\n'
        msg += body

    return msg


class PingbackFormulationError(Exception):
    def __init__(self, *args):
        # *args is used to get a list of the parameters passed in
        self.args = [a for a in args]


class PingbackSentError(Exception):
    pass


#
#   PROV-AQ functions
#
class ProvAqPingback:
    def __init__(self, entity_uri, instance_endpoint, sparql_endpoint):
        self.entity_uri = entity_uri
        self.instance_endpoint = instance_endpoint
        self.sparql_endpoint = sparql_endpoint
        self.uri_list = self._make_uri_list()
        self.further_links = self._make_further_links()
        self.pingback_msg = self._generate_msg()

    def _make_uri_list(self):
        # PROV-AQ wants RESTful URIs that lead to provenance for <entity_uri>
        # PROMS Server can only give a PROMS Server query URI that give PROV provenance for <entity_uri>
        return ['%(instance_endpoint)s?_uri=%(entity_uri_encoded)s&_view=prov&_format=text/turtle' % {
            'instance_endpoint': self.instance_endpoint,
            'entity_uri_encoded': uriparse.quote_plus(self.entity_uri)
        }]

    def _make_further_links(self):
        # PROV-AQ wants links to either static or queryable provenance for any other entity URI
        # PROMS Server chooses to only give:
        #   links for this entity - since other cnadidates for pingbacks are handled by other generated messages
        #   has_query_service - since the PROV-AQ message body will already contain the has_provenance data
        return [
            {
                'resource': self.entity_uri,
                'rel': 'has_query_service',
                'anchor': self.sparql_endpoint
            }
        ]

    def _make_link_headers(self):
        """
        Makes the slightly tircky HTTP Link header, if any

        :param further_links: a list of dicts with 'resource', 'rel', & 'anchor' properties, all URIs
        :return: a string
        """
        link_header_content = ''
        count = 0
        for further_link in self.further_links:
            if not is_a_uri(further_link['anchor']):
                raise PingbackFormulationError('Every anchor in a further_links array must be a valid URI')
            else:
                link_header_content += '<' + further_link['resource'] + '>; ' +\
                                    'rel="http://www.w3.org/ns/prov#' + further_link['rel'] + '"; ' +\
                                    'anchor="' + further_link['anchor'] + '",'
            count += 1
        return link_header_content[:-1]  # remove last ','

    def _generate_msg(self):
        headers = {'Content-Type': 'text/uri-list'}

        # if further links is set, iterate through them and create appropriate Link headers
        if self.further_links is not None:
            headers['Link'] = self._make_link_headers()

        # join the URIs into a string for the message body
        if self.uri_list is not None:
            body = '\n'.join(self.uri_list)  # the standard says CRLF (\r\n), not just \n
        else:
            # if we have no URIs, set the body to None and set a Content-Length header of zero
            body = None
            headers['Content-Length'] = '0'

        return {
            'headers': headers,
            'body': body
        }

    def send(self, pingback_target_uri):
        """
        Generates and posts a PROV-AQ pingback message

        Messages formulated according to http://www.w3.org/TR/prov-aq/#provenance-pingback, specifically generator 12, 13 & 14
        :param pingback_target_uri: a URI, to where the pingback is sent
        :param uri_list: a list object of URIs
        :param further_links: a list of dicts with 'resource', 'rel', & 'anchor' properties, all URIs
        :return: True or an error message
        """
        # send the post, as per http://www.w3.org/TR/prov-aq/
        r = requests.post(pingback_target_uri, data=self.pingback_msg['body'], headers=self.pingback_msg['headers'])
        result = (r.status_code == 204)
        if result:
            return True
        else:
            raise PingbackSentError('status_code: %s, message: %s' % (r.status_code, r.content))

    def send_dummy(self, pingback_target_uri):
        print('dummy sending PROV-AQ to %s' % pingback_target_uri)
        print('----------------------------------------')
        print(self.pingback_msg['headers'])
        print(self.pingback_msg['body'])
        print('----------------------------------------')


#
#   PROMS functions
#
class PromsPingback:
    def __init__(self, entity_uri, instance_endpoint):
        self.entity_uri = entity_uri
        self.instance_endpoint = instance_endpoint
        self.pingback_msg = self._generate_proms_msg()

    def _generate_proms_msg(self):
        # get the PROV view of this entity in PROMS, since it must have already been stored, given the incoming Report
        # handling sequence. This will fuse provenance from this report with provenance from all other sources for this
        # Entity if already in the provenance database thus updating on any previous pingbacks already sent for this
        # Entity
        query_uri = '%(instance_endpoint)s?_uri=%(entity_uri_encoded)s&_view=prov&_format=text/turtle' % {
            'instance_endpoint': self.instance_endpoint,
            'entity_uri_encoded': uriparse.quote_plus(self.entity_uri)
        }
        print(query_uri)
        r = requests.get(query_uri)
        if r.status_code == 200:
            return {
                'headers': {'Content-Type': 'text/turtle'},
                'body': r.content
            }
        else:
            raise Exception('Query back to PROMS for entity provenance failed: %s' % r.content)

    def send(self, pingback_target_uri):
        """
        Generates and posts a PROMS pingback message

        :param pingback_target_uri: a URI, to where the pingback is sent
        :param pingback_msg: an RDF file, in one of the allowed formats and conformant with the PROMS pingback message spec
        :param mimetype: the mimetype of the RDF file being sent
        :return: True or an error message
        """
        # send the post
        try:
            r = requests.post(
                pingback_target_uri,
                data=self.pingback_msg['body'],
                headers=self.pingback_msg['headers']
            )
            if r.status_code == 201:
                return [True, r.content]
            else:
                return [False, r.content]
        except Exception as e:
            return [False, e.message]

    def send_dummy(self, pingback_target_uri):
        print('dummy sending PROMS to %s' % pingback_target_uri)
        print('----------------------------------------')
        print(self.pingback_msg['headers'])
        print(self.pingback_msg['body'])
        print('----------------------------------------')
