from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, RDFS, XSD, Namespace, Literal
import settings
from modules.ldapi import LDAPI


class RegisterRenderer:
    def __init__(self, request, uri, register):
        self.request = request
        self.uri = uri
        self.register = register
        self.g = None

    def render_view_format(self, view, mimetype):
        if view == 'reg':
            # is an RDF format requested?
            if mimetype in LDAPI.get_rdf_mimetypes_list():
                # it is an RDF format so make the graph for serialization
                self._make_dpr_graph(view)
                rdflib_format = LDAPI.get_rdf_parser_for_mimetype(mimetype)
                return Response(
                    self.g.serialize(format=rdflib_format),
                    status=200,
                    mimetype=mimetype
                )
            elif mimetype == 'text/html':
                return render_template(
                    'class_register.html',
                    class_name=self.request.args.get('_uri'),
                    register=self.register
                )
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

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
