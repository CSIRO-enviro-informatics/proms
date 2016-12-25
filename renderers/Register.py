from flask import Response, render_template
from ldapi import LDAPI
import settings
from rdflib import Graph, URIRef, RDF, RDFS, XSD, Namespace, Literal


class RegisterRenderer:
    def __init__(self, request, uri, register):
        self.request = request
        self.uri = uri
        self.register = register
        self.g = None

    def render_view_format(self, view, rdf_format):
        if view == 'reg':
            # is an RDF format requested?
            if rdf_format in [item[0] for item in LDAPI.MIMETYPES_PARSERS]:
                # it is an RDF format so make the graph for serialization
                self._make_dpr_graph(view)
                rdflib_format = [item[1] for item in LDAPI.MIMETYPES_PARSERS if item[0] == rdf_format][0]
                return Response(
                    self.g.serialize(format=rdflib_format),
                    status=200,
                    mimetype=rdf_format
                )
            elif rdf_format == 'text/html':
                return render_template(
                    'class_register.html',
                    class_name=self.request.args.get('uri'),
                    register=self.register,
                    web_subfolder=settings.WEB_SUBFOLDER
                )
        else:
            return Response('The requested model view is not valid for this class', status=400, mimetype='text/plain')

    def _make_dpr_graph(self, model_view):
        self.g = Graph()

        if model_view == 'default' or model_view == 'reg' or model_view is None:
            # make the static part of the graph
            REG = Namespace('http://purl.org/linked-data/registry#')
            self.g.bind('reg', REG)

            self.g.add((URIRef(self.request.url), RDF.type, REG.Register))

            # add all the items
            for item in self.register:
                self.g.add((URIRef(item['uri']), RDF.type, URIRef(self.uri)))
                self.g.add((URIRef(item['uri']), RDFS.label, Literal(item['label'], datatype=XSD.string)))
                self.g.add((URIRef(item['uri']), REG.register, URIRef(self.request.url)))
