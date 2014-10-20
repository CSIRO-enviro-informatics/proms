import requests
import settings


def get_proms_html_header():
    html = requests.get('http://scikey.org/theme/template-header.inc').text

    nav = open(settings.HOME_DIR + settings.STATIC_DIR + 'nav.html', 'r').read()
    html = html.replace('<?php include $nav ?>', nav)

    return html


def get_proms_html_footer():
    html = requests.get('http://scikey.org/theme/template-footer.inc').text

    return html