from flask import Response, render_template

import database.get_things
import settings
import model.ReportingSystem
from modules.ldapi import LDAPI


class ActivityRenderer:
    def __init__(self, g, uri):
        # load Entity data from given graph
        self.g = g
        self.uri = uri

    def render_view_format(self, view, mimetype):
        """
        Renders a model and format of an Activity

        No validation is needed as the model and format for an Activity are pre-validated before this class is
        instantiated
        :param view: An allowed model model of an Activity
        :param mimetype: An allowed format of an Activity
        :return: A Flask Response object
        """
        if view == 'neighbours':
            # no work to be done as we have already loaded the triples
            if mimetype in LDAPI.get_rdf_mimetypes_list():
                return Response(
                    self.g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(mimetype)),
                    status=200,
                    mimetype=mimetype
                )
            elif mimetype == 'text/html':
                return render_template(
                    'class_activity.html',
                    reportingsystem=model.ReportingSystem.get_reportingsystem(self.uri),
                    web_subfolder=settings.WEB_SUBFOLDER
                )
