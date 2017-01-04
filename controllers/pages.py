"""
HTTP routes for basic HTML pages
"""
import os
from flask import Blueprint, render_template, send_from_directory, request, Response
import settings
import pages_functions
pages = Blueprint('pages', __name__)


@pages.route('/')
def home():
    # TODO: add a GetCapabilities function here
    if request.args.get('_view') or request.args.get('request') or request.args.get('REQUEST'):
        return Response(
            pages_functions.get_capabilities(),
            status=200,
            mimetype='application/xml'
        )

    return render_template(
        'page_index.html',
        web_subfolder=settings.WEB_SUBFOLDER
    )


@pages.route('/about')
def about():
    #logging.log(logging.INFO, '/about')
    return render_template(
        'page_about.html',
        web_subfolder=settings.WEB_SUBFOLDER,
        version=settings.VERSION
    )


@pages.route('/api')
def api():
    return render_template(
        'page_api.html',
        web_subfolder=settings.WEB_SUBFOLDER
    )


@pages.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(settings.HOME_DIR, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon'
    )


@pages.app_errorhandler(404)
def page_not_found(e):
    return render_template(
        'error_404.html',
        web_subfolder=settings.WEB_SUBFOLDER
    ), 404


@pages.app_errorhandler(405)
def page_not_found(e):
    return render_template(
        'error_405.html',
        web_subfolder=settings.WEB_SUBFOLDER
    ), 405
