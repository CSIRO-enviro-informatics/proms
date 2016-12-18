from flask import Response, render_template
from ldapi import LDAPI
import functions
import settings


class ReportingSystemRenderer:
    def __init__(self, g, uri):
        # load Entity data from given graph
        self.g = g
        self.uri = uri

    def render_view_format(self, view, format):
        """
        Renders a view and format of an ReportingSystem

        No validation is needed as the view and format for an ReportingSystem are pre-validated before this class is
        instantiated
        :param view: An allowed model view of an ReportingSystem
        :param format: An allowed format of an ReportingSystem
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
                    'class_reportingsystem.html',
                    reportingsystem=functions.get_reportingsystem_dict(self.uri),
                    web_subfolder=settings.WEB_SUBFOLDER
                )
        # elif view == 'prov':
        #     # remove all the non-PROV-O (and RDF) triples
        #     self.g.update(
        #         '''
        #         DELETE { ?s ?p ?o }
        #         WHERE {
        #             ?s ?p ?o .
        #             FILTER (!REGEX(STR(?p), "http://www.w3.org/ns/prov#") &&
        #                 !(STR(?p) = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"))
        #         }
        #         '''
        #     )
        #     if format in LDAPI.MIMETYPES_PARSERS.iterkeys():
        #         return Response(
        #             self.g.serialize(format=LDAPI.MIMETYPES_PARSERS.get(format)),
        #             status=200,
        #             mimetype=format
        #         )
        #     else:  # HTML
        #         return render_template('class_reportingrystem_prov.html')
