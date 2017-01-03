import logging
from flask import Flask
from werkzeug.routing import BaseConverter
import settings
from controllers import objects, pages, api
import urllib
# from secure.api import api -- not implemented yet

app = Flask(__name__)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

# regex paths
app.url_map.converters['regex'] = RegexConverter
app.url_map.strict_slashes = True

app.register_blueprint(pages.pages)
app.register_blueprint(api.api)
app.register_blueprint(objects.modelx)
# app.register_blueprint(api) -- rename this from 'api' to secure or something

# add functions to the Jinja2 templates to allow URIs to be displayed nicely
app.jinja_env.filters['quote_plus'] = lambda u: urllib.quote_plus(u)
app.jinja_env.filters['unquote_plus'] = lambda u: urllib.unquote_plus(u)

# run the app
if __name__ == '__main__':
    logging.basicConfig(
        filename=settings.LOGFILE,
        level=settings.LOG_LEVEL,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s'
    )

    #logging.log(logging.INFO, 'PROMS Started, %(host)s:%(port)d' % {'host': settings.BASE_URI, 'port': settings.PORT})

    # prod logging
    # handler = logging.FileHandler(settings.LOGFILE)
    # handler.setLevel(settings.LOG_LEVEL)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    # app.logger.addHandler(handler)

    app.run(
        host=settings.HOST,
        port=settings.PORT,
        threaded=True,
        debug=settings.DEBUG
    )
