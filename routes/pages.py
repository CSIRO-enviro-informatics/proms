"""
HTTP routes for basic HTML pages
"""
import os
from flask import Blueprint, render_template, send_from_directory
import settings
pages = Blueprint('pages', __name__)


@pages.route('/')
def home():
    return render_template(
        'page_index.html',
        web_subfolder=settings.WEB_SUBFOLDER
    )


@pages.route('/about')
def about():
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
    ), 404