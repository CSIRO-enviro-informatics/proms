from flask import Response, render_template
from ldapi import LDAPI
import functions
import settings
import functions_sparqldb
from rdflib import Graph


class EntityRenderer:
    def __init__(self, g, uri):
        # load Entity data from given graph
        self.g = g
        self.uri = uri

    def get_graph(self):
        """
        Returns the graph of an object in the graph database

        :param uri: the URI of something in the graph database
        :return: an RDF Graph
        """
        uri = self.uri
        if uri is not None:
            r = functions_sparqldb.query_turtle(q)
            # a uri query string argument was supplied was supplied but it was not the URI of something in the graph
            g = Graph().parse(data=r, format='turtle')
            if len(g) == 0:
                # try a named graph
                r = functions_sparqldb.query_turtle(
                    'CONSTRUCT { <' + uri + '> ?p ?o } WHERE { GRAPH ?g { <' + uri + '> ?p ?o }}'
                )
                # a uri query string argument was supplied was supplied but it was not the URI of something in the graph
                g = Graph().parse(data=r, format='turtle')

                if len(g) == 0:
                    # nothing found
                    return False
                else:
                    return g
            else:
                return g
                # no uri query string argument was supplied
        else:
            return False

    def render_view_format(self, view, format):
        """
        Renders a view and format of an Entity

        No validation is needed as the view and format for an Entity are pre-validated before this class is instantiated
        :param view: An allowed model view of an Entity
        :param format: An allowed format of an Entity
        :return: A Flask Response object
        """
        if view == 'neighbours':
            # at this point, we only have the basic triples for the Entity but we need all its links to other things
            # e.g. Activities & Agents & other Entities

            # Activities related to this Entity
            q2 = '''
                    PREFIX prov: <http://www.w3.org/ns/prov#>
                    PREFIX dc: <http://purl.org/dc/elements/1.1/>
                    CONSTRUCT {
                        ?s ?p ?o
                    }
                    WHERE {
                        GRAPH ?g {
                            ?a a prov:Activity .
                            ?a ?p <''' + self.uri + ''''> .
                            <''' + self.uri + ''''> ?p ?a .
                            ?a dc:title ?t .
                            #OPTIONAL { ?s (prov:used|prov:generated) <''' + self.uri + ''''1> }
                            #OPTIONAL { <''' + self.uri + ''''> prov:wasGeneratedBy ?s }
                        }
                    }
            '''
            g2 = Graph().parse(data=functions_sparqldb.query_turtle(q2), format='turtle')
            self.g = self.g + g2

            for s, p, o in self.g:
                print str(s) + ' ' + str(p) + ' ' + str(o)

            # other Entities related to this Entity
            q3 = '''
                    PREFIX prov: <http://www.w3.org/ns/prov#>
                    PREFIX dc: <http://purl.org/dc/elements/1.1/>
                    CONSTRUCT {
                        ?s ?p ?o
                    }
                    WHERE {
                        GRAPH ?g {
                            ?s a prov:Entity .
                            ?s ?p <''' + self.uri + ''''> .
                            OPTIONAL { ?s (prov:used|prov:generated) <''' + self.uri + ''''> }
                            OPTIONAL { <''' + self.uri + ''''> prov:wasGeneratedBy ?s }
                        }
                    }
            '''
            # TODO: show wasDerivedFrom in SVG

            g3 = Graph().parse(data=functions_sparqldb.query_turtle(q3), format='turtle')
            self.g = self.g + g3

            if format in LDAPI.MIMETYPES_PARSERS.iterkeys():
                return Response(
                    self.g.serialize(format=LDAPI.MIMETYPES_PARSERS.get(format)),
                    status=200,
                    mimetype=format
                )
            elif format == 'text/html':
                return render_template(
                    'class_entity.html',
                    entity=functions.get_entity_dict(self.uri),
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
        #         return render_template(
        #             'class_entity_prov.html',
        #             entity=functions.get_entity_dict(self.uri),
        #             web_subfolder=settings.WEB_SUBFOLDER
        #         )
        # elif view == 'ancestors':
        #     # get all ancestors from database graph
        #     q = '''
        #
        #     '''
        #     # TODO: need reasoning in here
        #     pass
        # elif view == 'descendants':
        #     # get all descendants from database graph
        #     # TODO: need reasoning in here
        #     pass
        elif view == 'test':
            q = '''
            PREFIX proms: <http://promsns.org/def/proms#>
            SELECT * WHERE { GRAPH ?g {
                { ?s a proms:Report }
                UNION
                { ?s a proms:BasicReport }
                UNION
                { ?s a proms:ExternalReport }
                UNION
                { ?s a proms:InternalReport }
              }
            }
            '''
            for s, p, o in self.g:
                print str(s) + ' ' + str(p) + ' ' + str(o)
