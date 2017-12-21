from .renderer import Renderer
from flask import Response, render_template
import _database
import urllib.parse as uriparse
from modules.ldapi import LDAPI
from rdflib import Graph, URIRef, Literal, Namespace


class ClassRenderer(Renderer):
    def __init__(self, uri, endpoints):
        Renderer.__init__(self, uri, endpoints)

        self.uri_encoded = uriparse.quote_plus(uri)
        self.label = None
        self.aobo = None
        self.aobo_label = None
        self.script = None

    def render(self, view, mimetype):
        if mimetype == 'text/html':
            self._get_details()
            return self._html()
        else:
            self._get_details()
            return Response(
                self._rdf().serialize(format=LDAPI.get_rdf_parser_for_mimetype(mimetype)),
                mimetype=mimetype
            )

    def _rdf(self):
        query = '''
                 SELECT * WHERE {
                    <%(uri)s>  ?p ?o .
                 }
         ''' % {'uri': self.uri}
        g = Graph()
        g.bind('prov', Namespace('http://www.w3.org/ns/prov#'))
        for r in _database.query(query)['results']['bindings']:
            if r['o']['type'] == 'literal':
                g.add((URIRef(self.uri), URIRef(r['p']['value']), Literal(r['o']['value'])))
            else:
                g.add((URIRef(self.uri), URIRef(r['p']['value']), URIRef(r['o']['value'])))

        query2 = '''
                 SELECT * WHERE {
                    ?s ?p <%(uri)s> .
                 }
         ''' % {'uri': self.uri}
        for r in _database.query(query2)['results']['bindings']:
            g.add((URIRef(r['s']['value']), URIRef(r['p']['value']), URIRef(self.uri)))

        return g

    def _html(self):
        """Returns a simple dict of Entity properties for use by a Jinja template"""
        ret = {
            'uri': self.uri,
            'uri_encoded': self.uri_encoded,
            'label': self.label,
            'aobo': self.aobo,
            'aobo_label': self.aobo_label
        }

        prov_data = self._prov_rdf().serialize(format='turtle')

        return render_template(
            'class_entity_prov.html',
            agent=ret,
            prov_data=prov_data
        )

    def _get_details(self):
        """ Get the details (label only) for an Class from an RDF triplestore"""
        # formulate the query
        query = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE { GRAPH ?g {
                <%(uri)s>
                    rdfs:label ?label .
              }
            }
            ''' % {'uri': self.uri}

        # run the query
        class_details = _database.query(query)

        # extract results into instance vars
        if 'results' in class_details:
            if len(class_details['results']['bindings']) > 0:
                ret = class_details['results']['bindings'][0]
                self.label = ret['label']['value']

    def _export_for_html_template(self):
        """Returns a simple dict of Class properties for use by a Jinja template"""
        ret = {
            'uri': self.uri,
            'uri_encoded': self.uri_encoded,
            'label': self.label
        }

        if self.script is not None:
            ret['script'] = self.script

        return ret