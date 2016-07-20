import logging
import settings
from flask import Flask
from routes import routes
from api import api

app = Flask(__name__)


from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

#regex paths
app.url_map.converters['regex'] = RegexConverter


#import the routes in routes.py
app.register_blueprint(routes)
app.register_blueprint(api)


#run the app
if __name__ == '__main__':
    logging.basicConfig(filename=settings.LOGFILE,
                        level=logging.ERROR,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s')

    app.run(host=settings.HOST,
            port=settings.PORT,
            threaded=True,
            debug=settings.DEBUG)
