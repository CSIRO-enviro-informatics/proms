from flask import Response, render_template
import settings


# TODO: add in a resumption token equiv (start, length, index property) just like OAI-PMH & CSW& GitHub (Link headers)
class LDAPI:
    """
    A class containing static functions to assist with building a Linked Data API

    This class is issued as a Python file, rather than a Git submodule so check the version number before use!

    Version 1.0
    """

    # maps HTTP MIMETYPES to rdflib's RDF parsing formats
    MIMETYPES_PARSERS = [
        ('text/turtle', 'turtle'),
        ('application/rdf+xml', 'xml'),
        ('application/rdf+json', 'json-ld'),
        ('application/json', 'json-ld'),
        ('text/ntriples', 'nt'),
        ('text/nt', 'nt'),
        ('text/n3', 'nt')
    ]

    def __init__(self):
        pass

    @staticmethod
    def get_rdf_mimetypes_list():
        return [item[0] for item in LDAPI.MIMETYPES_PARSERS]

    @staticmethod
    def get_rdf_parser_for_mimetype(mimetype):
        return [item[1] for item in LDAPI.MIMETYPES_PARSERS if item[0] == mimetype][0]

    @staticmethod
    def get_mimetype_for_rdf_parser(rdf_parser):
        return [item[0] for item in LDAPI.MIMETYPES_PARSERS if item[1] == rdf_parser][0]

    @staticmethod
    def get_file_extension(mimetype):
        """
        Matches the file extension to MIME types

        :param mimetype: an HTTP mime type
        :return: a string
        """
        file_extension = {
            'text/turtle': '.ttl',
            'application/rdf+xml': '.rdf',
            'application/rdf+json': '.json',
            'application/xml': '.xml',
            'text/xml': '.xml',
        }

        return file_extension[mimetype]

    @staticmethod
    def an_int(s):
        """
        Safely (no Error throw) tests to see whether a string can be itnerpreted as an int

        :param s: string
        :return: boolean
        """
        if s is not None:
            try:
                int(s)
                return True
            except ValueError:
                return False
        else:
            return False

    @staticmethod
    def valid_view(view, views_formats):
        """
        Determines whether a requested model model is valid and, if it is, it returns it

        :return: model name (string) or False
        """
        if view is not None:
            if view in views_formats.iterkeys():
                return view
            else:
                raise LdapiParameterError(
                    'The _view parameter is invalid. For this object, it must be one of {0}.'
                    .format(', '.join(views_formats.iterkeys()))
                )
        else:
            # views_formats will give us the default model
            return views_formats['default']

    @staticmethod
    def valid_format(format, view, views_formats):
        """
        Determines whether a requested format for a particular model model is valid and, if it is, it returns it

        :return: model name (string) or False
        """
        if format is not None:
            if format.replace(' ', '+') in views_formats[view]:
                return format.replace(' ', '+')
            else:
                raise LdapiParameterError(
                    'The _format parameter is invalid. For this model model, format should be one of {0}.'
                        .format(', '.join(views_formats[view]))
                )
        else:
            # HTML is default
            return 'text/html'

    @staticmethod
    def get_valid_view_and_format(view, format, views_formats):
        """
        If both the model and the format are valid, return them
        :param view: the model model parameter
        :param format: the MIMETYPE format parameter
        :param views_formats: the allowed model and their formats in this instance
        :return: valid model and format
        """
        view = LDAPI.valid_view(view, views_formats)
        format = LDAPI.valid_format(format, view, views_formats)
        if view and format:
            # return valid model and format
            return view, format

    @staticmethod
    def client_error_Response(error_message):
        return Response(
            error_message,
            status=400,
            mimetype='text/plain'
        )


class LdapiParameterError(ValueError):
    pass
