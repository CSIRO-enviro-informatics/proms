"""
This file contains all the HTTP routes for classes from the PROMS Ontology, such as Samples and the Sample Register
"""

from flask import Blueprint, request, render_template
from ldapi import LDAPI, LdapiParameterError
from requests.exceptions import ConnectionError
from routes.api_functions import Response_client_error
import instances_classes_functions
import api_functions
import database
import settings
import renderers.Register

inst_cls = Blueprint('inst_cls', __name__)


@inst_cls.route('/register')
def register():
    """
    Responds with a Register view response for classes listed in the graph

    Supported classes statically loaded from classes_views_formats.json
    In the future, we will dynamically work out which classes are supported.

    :param class_name: the name of a class of object in the graph db
    :return: an HTTP message based on a particular view and format of the class
    """

    # check for a class URI
    uri = request.args.get('uri')
    # ensure the class URI is one of the classes in the views_formats
    class_uris = instances_classes_functions.get_class_uris()
    if uri not in class_uris:
        return Response_client_error(
            'No URI of a class in the provenance database was supplied. Expecting a query string argument \'uri\' '
            'equal to one of the following: ' +
            ', '.join(class_uris)
        )

    # validate this request's view and format
    class_uri = 'http://purl.org/linked-data/registry#Register'
    views_formats = instances_classes_functions.get_classes_views_formats().get(class_uri)
    try:
        view, mime_format = LDAPI.get_valid_view_and_format(
            request.args.get('_view'),
            request.args.get('_format'),
            views_formats
        )
    except LdapiParameterError, e:
        return Response_client_error(e)

    # if alternates view, return this info from file
    if view == 'alternates':
        return api_functions.render_alternates_view(class_uri, None, views_formats, mime_format)

    # get the register of this class of thing from the provenance database
    try:
        class_register = database.get_class_register(uri)
    except ConnectionError:
        return render_template('error_db_connection.html'), 500

    # since everything's valid, use the Renderer to return a response
    return renderers.Register.RegisterRenderer(request, uri, class_register).render_view_format(view, mime_format)


@inst_cls.route('/register/<string:class_name>/')
def register_name(class_name):
    """
    Responds with a Register view response for classes listed in the graph

    Supported classes statically loaded from classes_views_formats.json
    In the future, we will dynamically work out which classes are supported.

    :param class_name: the name of a class of object in the graph db
    :return: an HTTP message based on a particular view and format of the class
    """

    # check if class name given corresponds to a supported class name
    supported_classes = sorted(instances_classes_functions.get_classes())
    if class_name not in supported_classes:
        return api_functions.Response_client_error(
            'class_name must be one of ' + ', '.join(supported_classes) + '.')

    # get the class URI for this class_name
    class_uri = instances_classes_functions.get_class_uri(class_name)

    # get the register of this class of thing from the provenance database
    try:
        register = database.get_things.get_class_register(class_uri)
    except ConnectionError:
        return render_template('error_db_connection.html'), 500

    return render_template(
        'class_register.html',
        class_name=class_name,
        register=register,
        web_subfolder=settings.WEB_SUBFOLDER
    )


@inst_cls.route('/instance')
def instance():
    """
    Responds with one of a number of HTTP responses according to an allowed view and format of this object in the graph

    :return: and HTTP response
    """
    # must have the URI of an object in the graph
    instance_uri = request.args.get('uri')
    g = database.get_class_object_graph(instance_uri)
    if not g:
        return Response_client_error(
            'No URI of an object in the provenance database was supplied. Expecting a query string argument \'uri\'.')

    # the URI is of something in the graph so now we validate the requested view and format
    # find the class of the URI
    for s, p, o in g:
        if str(p) == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
            # validate this request's view and format
            class_uri = str(o)
            views_formats = instances_classes_functions.get_classes_views_formats().get(class_uri)
            try:
                view, mime_format = LDAPI.get_valid_view_and_format(
                            request.args.get('_view'),
                            request.args.get('_format'),
                            views_formats
                        )

                # if alternates view, return this info from file
                if view == 'alternates':
                    return api_functions.render_alternates_view(class_uri, instance_uri, views_formats, mime_format)
                else:
                    # all the relevant Python class for the graph class and render the particular view and format
                    # no need for further validation as instance_uri, view & format are already validated
                    renderer = getattr(__import__('renderers'), views_formats['renderer'])
                    return renderer(g, instance_uri).render_view_format(view, mime_format)

            except LdapiParameterError, e:
                return Response_client_error(e)
