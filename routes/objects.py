"""
This file contains all the HTTP routes for classes from the PROMS Ontology, such as Samples and the Sample Register
"""
import urllib
import model
from flask import Blueprint, request, render_template, url_for
from requests.exceptions import ConnectionError
import api_functions
import database
import objects_functions
from routes.api_functions import Response_client_error
from modules.ldapi import LDAPI, LdapiParameterError
modelx = Blueprint('modelx', __name__)


@modelx.route('/register')
def register():
    """
    Responds with a Register model response for classes listed in the graph

    Supported classes statically loaded from classes_views_formats.json
    In the future, we will dynamically work out which classes are supported.

    :param class_name: the name of a class of object in the graph db
    :return: an HTTP message based on a particular model and format of the class
    """

    # check for a class URI
    uri = request.args.get('_uri')
    # ensure the class URI is one of the classes in the views_formats
    class_uris = objects_functions.get_class_uris()
    if uri not in class_uris:
        return Response_client_error(
            'No URI of a class in the provenance database was supplied. Expecting a query string argument \'_uri\' '
            'equal to one of the following: ' +
            ', '.join(class_uris)
        )

    # validate this request's model and format
    class_uri = 'http://purl.org/linked-data/registry#Register'
    views_formats = objects_functions.get_classes_views_formats().get(class_uri)
    try:
        view, mime_format = LDAPI.get_valid_view_and_format(
            request.args.get('_view'),
            request.args.get('_format'),
            views_formats
        )
    except LdapiParameterError, e:
        return Response_client_error(e)

    # if alternates model, return this info from file
    if view == 'alternates':
        del views_formats['renderer']
        return api_functions.render_alternates_view(uri, urllib.quote_plus(uri), None, None, views_formats, mime_format)

    # get the register of this class of thing from the provenance database
    try:
        class_register = database.get_class_register(uri)
    except ConnectionError:
        return render_template('error_db_connection.html'), 500

    # since everything's valid, use the Renderer to return a response
    endpoints = {
        'instance': url_for('.instance'),
        'sparql': url_for('api.sparql')
    }
    return model.RegisterRenderer(request, uri, endpoints, class_register).render(view, mime_format)


@modelx.route('/register/<string:class_name>/')
def register_name(class_name):
    """
    Responds with a Register model response for classes listed in the graph

    Supported classes statically loaded from classes_views_formats.json
    In the future, we will dynamically work out which classes are supported.

    :param class_name: the name of a class of object in the graph db
    :return: an HTTP message based on a particular model and format of the class
    """

    # check if class name given corresponds to a supported class name
    supported_classes = sorted(objects_functions.get_classes())
    if class_name not in supported_classes:
        return api_functions.Response_client_error(
            'class_name must be one of ' + ', '.join(supported_classes) + '.')

    # get the class URI for this class_name
    class_uri = objects_functions.get_class_uri(class_name)

    # get the register of this class of thing from the provenance database
    try:
        register = database.get_things.get_class_register(class_uri)
    except ConnectionError:
        return render_template('error_db_connection.html'), 500

    return render_template(
        'class_register.html',
        class_name=class_name,
        register=register
    )


@modelx.route('/instance')
def instance():
    """
    Responds with one of a number of HTTP responses according to an allowed model and format of this object in the graph

    :return: and HTTP response
    """
    # must have the URI of an object in the graph
    instance_uri = request.args.get('_uri')
    try:
        g = database.get_class_object_graph(instance_uri)

        if not g:
            return Response_client_error(
                'No URI of an object in the provenance database was supplied. '
                'Expecting a query string argument \'_uri\'.')
    except ConnectionError:
        return render_template('error_db_connection.html'), 500

    # the URI is of something in the graph so now we validate the requested model and format
    # find the class of the URI
    for s, p, o in g:
        if str(p) == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
            # validate this request's model and format
            class_uri = str(o)
            views_formats = objects_functions.get_classes_views_formats().get(class_uri)
            try:
                view, mime_format = LDAPI.get_valid_view_and_format(
                            request.args.get('_view'),
                            request.args.get('_format'),
                            views_formats
                        )

                # if alternates model, return this info from file
                if view == 'alternates':
                    instance_uri_encoded = urllib.quote_plus(request.args.get('_uri'))
                    class_uri_encoded = urllib.quote_plus(class_uri)
                    del views_formats['renderer']
                    return api_functions.render_alternates_view(class_uri, class_uri_encoded, instance_uri, instance_uri_encoded, views_formats, mime_format)
                else:
                    # chooses a class to render this instance based on the specified renderer in
                    # classes_views_formats.json
                    # no need for further validation as instance_uri, model & format are already validated
                    renderer = getattr(__import__('model'), views_formats['renderer'])
                    endpoints = {
                        'instance': url_for('.instance'),
                        'sparql': url_for('api.sparql')
                    }
                    return renderer(
                        instance_uri,
                        endpoints
                    ).render(view, mime_format)

            except LdapiParameterError, e:
                return Response_client_error(e)
