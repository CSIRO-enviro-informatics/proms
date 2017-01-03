import json
import urllib
from flask import render_template
import settings
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()


def get_classes_views_formats():
    """
    Caches the graph_classes JSON file in memory
    :return: a Python object parsed from the classes_views_formats.json file
    """
    cvf = cache.get('classes_views_formats')
    if cvf is None:
        cvf = json.load(open('controllers/classes_views_formats.json'))
        # times out never (i.e. on app startup/shutdown
        cache.set('classes_views_formats', cvf)
    return cvf


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


def get_classes():
    cvf = get_classes_views_formats()
    classes = []
    for c in cvf.iterkeys():
        if not c.startswith('_'):
            classes.append(c.split('#')[1])

    return classes


def get_class_uri(class_name):
    cvf = get_classes_views_formats()
    for c in cvf.iterkeys():
        if not c.startswith('_'):
            if c.split('#')[1] == class_name:
                return c


def get_class_uris():
    cvf = get_classes_views_formats()
    classes = []
    for c in cvf.iterkeys():
        if not c.startswith('_'):
            classes.append(c)
    return classes
