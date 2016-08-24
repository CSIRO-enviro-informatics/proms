import logging
import settings
from flask import Flask
from routes import routes
from api import api
from werkzeug.routing import BaseConverter

app = Flask(__name__)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

# regex paths
app.url_map.converters['regex'] = RegexConverter
app.url_map.strict_slashes = True

# import the routes in routes.py
app.register_blueprint(routes)
app.register_blueprint(api)

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
