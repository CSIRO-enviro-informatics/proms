from flask import Response, render_template
from ldapi import LDAPI
import database.get_things
import settings


class ReportRenderer:
    def __init__(self, g, uri):
        # load Entity data from given graph
        self.g = g
        self.uri = uri

    def render_view_format(self, view, format):
        """
        Renders a view and format of an Report

        No validation is needed as the view and format for an Report are pre-validated before this class is
        instantiated
        :param view: An allowed model view of an Report
        :param format: An allowed format of an Report
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
                    'class_report.html',
                    report=database.get_things.get_report(self.uri),
                    web_subfolder=settings.WEB_SUBFOLDER
                )
