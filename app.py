import logging
from flask import Flask
from werkzeug.routing import BaseConverter
import settings
from routes import ont_classes, pages, api
# from secure.api import api -- not implemented yet

app = Flask(__name__)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

# regex paths
app.url_map.converters['regex'] = RegexConverter
app.url_map.strict_slashes = True

# import the routes in functions.py
app.register_blueprint(pages.pages)
app.register_blueprint(api.api)
app.register_blueprint(ont_classes.ont_classes)
# app.register_blueprint(functions)
# app.register_blueprint(api) -- rename this from 'api' to secure or something


# run the app
if __name__ == '__main__':
    logging.basicConfig(filename=settings.LOGFILE,
                        level=logging.ERROR,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s')

    app.run(host=settings.HOST,
            port=settings.PORT,
            threaded=True,
            debug=settings.DEBUG)
