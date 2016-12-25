from flask import Response, render_template

import database.get_things
from ldapi import LDAPI
from routes import functions_agents
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
            if format in [x[0] for x in LDAPI.MIMETYPES_PARSERS]:
                return Response(
                    self.g.serialize(format=LDAPI.MIMETYPES_PARSERS.get(format)),
                    status=200,
                    mimetype=[item[1] for item in LDAPI.MIMETYPES_PARSERS if item[0] == self.agent_mimetype][0]
                )
            elif format == 'text/html':
                return render_template(
                    'class_agent.html',
                    agent=database.get_things.get_agent(self.uri),
                    web_subfolder=settings.WEB_SUBFOLDER
                )
