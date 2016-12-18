from flask import Response, render_template
from ldapi import LDAPI
import functions
import settings


class AgentRenderer:
    def __init__(self, g, uri):
        # load Entity data from given graph
        self.g = g
        self.uri = uri

    def render_view_format(self, view, format):
        """
        Renders a view and format of an Agent

        No validation is needed as the view and format for an Agent are pre-validated before this class is
        instantiated
        :param view: An allowed model view of an Agent
        :param format: An allowed format of an Agent
        :return: A Flask Response object
        """
        if view == 'neighbours':
            # no work to be done as we have already loaded the triples
            if format in LDAPI.MIMETYPES_PARSERS.iterkeys():
                return Response(
                    self.g.serialize(format=LDAPI.MIMETYPES_PARSERS.get(format)),
                    status=200,
                    mimetype=format
                )
            elif format == 'text/html':
                return render_template(
                    'class_agent.html',
                    reportingsystem=functions.get_reportingsystem_dict(self.uri),
                    web_subfolder=settings.WEB_SUBFOLDER
                )
