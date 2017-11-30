"""
HTTP routes for basic HTML pages
"""
import os
from flask import Blueprint, render_template, send_from_directory, request, Response
import _config as conf
from requests.exceptions import ConnectionError
from controller import pages_functions
pages = Blueprint('pages', __name__)


@pages.route('/')
def home():
    if request.args.get('_view') or request.args.get('request') or request.args.get('REQUEST'):
        return Response(
            pages_functions.get_capabilities(),
            status=200,
            mimetype='application/xml'
        )

    return render_template(
        'page_index.html'
    )


@pages.route('/about')
def about():
    return render_template(
        'page_about.html',
        version=conf.VERSION
    )


@pages.route('/contents')
def contents():
    try:
        content_classes = pages_functions.get_contents_classes()
    except ConnectionError:
        return render_template('error_db_connection.html'), 500
    return render_template(
        'page_contents.html',
        content_classes=content_classes
    )


@pages.route('/api')
def api():
    return render_template(
        'page_api.html'
    )


@pages.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(conf.APP_DIR, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon'
    )


@pages.app_errorhandler(404)
def page_not_found(e):
    return render_template(
        'error_404.html'
    ), 404


@pages.app_errorhandler(405)
def page_not_found(e):
    return render_template(
        'error_405.html'
    ), 405
