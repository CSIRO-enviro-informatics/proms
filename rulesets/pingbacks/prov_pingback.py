from rulesets import RuleSet, Rule


class ProvPingback(RuleSet):
    def __init__(self, request):
        rules = []
        r1 = Header(request)
        rules.append(r1)
        r2 = Body(request)
        rules.append(r2)

        RuleSet.__init__(
            self,
            'PROV-AQ Pingback message',
            rules,
            None)  # dependent on PromsReport


class Header(Rule):
    def __init__(self, request):
        self.fail_reasons = []

        # not valid if Content-Type not set to text/uri-list
        if request.headers.get('Content-Type') != 'text/uri-list':
            self.fail_reasons.append(
                'The pingback message must have a content-type of \'text/uri-list\' defined in the HTTP header')

        # not valid if no Link header set and Content-Length == 0
        if not request.headers.get('Link') and int(request.headers.get('Content-Length')) == 0:
            self.fail_reasons.append(
                'The pingback message must have either a non-zero Content-Lenth or a Link header set')

        # validate each PROV-AQ Link header
        if request.headers.get('Link'):
            for link_header in request.headers.get('Link').split(','):
                link_header_valid = self.valid_provaq_link_header(link_header.trim())
                if not link_header_valid[0]:
                    self.fail_reasons.append(
                        'The Link header "{}" is not valid: {}'.format(link_header, link_header_valid[1])
                    )

        # determine passed due to any fail_reasons
        # if there are any failure reasons it means it's failed
        if self.fail_reasons:
            self.passed = False

        Rule.__init__(
            self,
            'PROV-AQ Header',
            'The pingback must have a valid PROV-AQ-specified header',
            'PROV-AQ',
            self.passed,
            self.fail_reasons,
            1,  # the number of individual test
            len(self.fail_reasons)  # the number of test failed
        )

    def valid_provaq_link_header(self, link_header):
        errors = []
        parts = link_header.split(';')
        if len(parts) != 3:
            return [False, 'does not have 3 parts']

        uri = str(parts[0].strip())

        if not uri.startswith('<') or not uri.endswith('>'):
            errors.append('the URI doesn\'t start with \'<\'and end with \'>\'')

        if not self.is_a_uri(uri.strip('<>')):
            errors.append('the URI is not a valid URI')

        rel = str(parts[1].strip())

        if not rel in ['rel="http://www.w3.org/ns/prov#has_provenance"', 'rel="http://www.w3.org/ns/prov#has_query_service"']:
            errors.append('the rel part must be either rel="http://www.w3.org/ns/prov#has_provenance" or rel="http://www.w3.org/ns/prov#has_query_service". You gave: {}'.format(rel))

        anchor = str(parts[2].strip())
        anchor_uri = anchor.replace('anchor="', '').replace('"', '')

        if not anchor.startswith('anchor="') or not anchor.endswith('"') or not self.is_a_uri(anchor_uri):
            errors.append('the anchor part needs to start with \'anchor=\' followed by a valid URI in double quotes')

        if errors:
            return [False, errors]
        else:
            return [True]

    def is_a_uri(self, uri_candidate):
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


class Body(Rule):
    def __init__(self, request):
        self.fail_reasons = []

        body = request.content

        # if content-length zero, don't allow content
        if int(request.headers.get('Content-Length')) == 0 and len(str(body).strip()) > 0:
            self.fail_reasons.append(
                'The Content-Length header indicates no content and yet there is body content')

        # if content, it needs to be a linbreak list of URIs only
        for line in body.split('\n'):
            if not self.is_a_uri(line.strip()):
                self.fail_reasons.append(
                    'The line {} is not a valid URI'.format(line))

        # determine passed due to any fail_reasons
        # if there are any failure reasons it means it's failed
        if self.fail_reasons:
            self.passed = False

        Rule.__init__(
            self,
            'PROV-AQ Body',
            'The pingback must have a valid PROV-AQ-specified body',
            'PROV-AQ',
            self.passed,
            self.fail_reasons,
            1,  # the number of individual test
            len(self.fail_reasons)  # the number of test failed
        )

    def is_a_uri(self, uri_candidate):
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