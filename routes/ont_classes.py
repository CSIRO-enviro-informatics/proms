"""
This file contains all the HTTP routes for classes from the PROMS Ontology, such as Samples and the Sample Register
"""
import settings
from flask import Blueprint, Response, request, render_template
from werkzeug.contrib.cache import SimpleCache
import json
from ldapi import LDAPI, LdapiParameterError
import functions_sparqldb
import urllib
from rdflib import Graph
from renderers import AgentRenderer
ont_classes = Blueprint('ont_classes', __name__)
cache = SimpleCache()


def get_classes_views_formats():
    """
    Caches the graph_classes JSON file in memory
    :return: a Python object parsed from the classes_views_formats.json file
    """
    cvf = cache.get('classes_views_formats')
    if cvf is None:
        cvf = json.load(open('routes/classes_views_formats.json'))
        # times out never (i.e. on app startup/shutdown
        cache.set('classes_views_formats', cvf)
    return cvf


def client_error_Response(error_message):
    return Response(
        error_message,
        status=400,
        mimetype='text/plain'
    )


def render_graph_class_templates_alternates(parent_template, uri, graph_class, graph_class_name, views_formats):
    return render_template(
        parent_template,
        base_uri=settings.BASE_URI,
        web_subfolder=settings.WEB_SUBFOLDER,
        view='alternates',
        uri=uri,
        graph_class=graph_class,
        graph_class_name=graph_class_name,
        placed_html=render_template(
            'view_alternates.html',
            uri=urllib.quote_plus(uri),
            views_formats=views_formats
        )
    )


def get_graph(uri):
    """
    Returns the graph of an object in the graph database

    :param uri: the URI of something in the graph database
    :return: an RDF Graph
    """
    if uri is not None:
        r = functions_sparqldb.query_turtle(
            'CONSTRUCT { <' + uri + '> ?p ?o } WHERE { <' + uri + '> ?p ?o }'
        )
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


@ont_classes.route('/register')
@ont_classes.route('/register/')
def class_register_missing():
    return Response(
        'You must specify a class name, /register{class_name}. class_name can be one of Report, ReportingSystem, '
        'Activity, Agent,  Entity, Person.',
        status=400,
        mimetype='text/plain'
    )


@ont_classes.route('/register/<string:class_name>/')
def class_register(class_name):
    """
    Responds with a Register view response for classes listed in the graph

    Supported classes statically loaded from classes_views_formats.json
    In the future, we will dynamically work out which classes are supported.

    :param class_name: the name of a class of object in the graph db
    :return: an HTTP message based on a particular view and format of the class
    """
    pass


@ont_classes.route('/object')
def graph_object():
    """
    Responds with one of a number of HTTP responses according to an allowed view and format of this object in the graph

    :return: and HTTP response
    """
    # must have the URI of an object in the graph
    uri = request.args.get('_uri')
    g = get_graph(uri)
    if not g:
        return client_error_Response(
            'No URI of an object in the graph database was supplied. Expecting a query string argument \'_uri\'.')

    # the URI is of something in the graph so now we validate the requested view and format
    # find the class of the URI
    for s, p, o in g:
        if str(p) == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
            graph_class = str(o)

            views_formats = get_classes_views_formats().get(graph_class)
            try:
                view, format = LDAPI.get_valid_view_and_format(
                            request.args.get('_view'),
                            request.args.get('_format'),
                            views_formats
                        )

                # select view and format
                if view == 'alternates':
                    # TODO: inform viewer about the default view
                    return render_graph_class_templates_alternates(
                        'class.html',
                        uri,
                        graph_class,
                        graph_class.split('/')[-1].split('#')[-1],
                        views_formats)
                else:
                    # all the relevant Python class for the graph class and render the particular view and format
                    # no need for further validation as uri, view & format are already validated
                    renderer = getattr(__import__('renderers'), views_formats['renderer'])
                    return renderer(g, uri).render_view_format(view, format)

            except LdapiParameterError, e:
                return client_error_Response(e)
