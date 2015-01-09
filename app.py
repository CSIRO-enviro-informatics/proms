import logging
import settings
from flask import Flask
from routes import routes
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


#run the app
if __name__ == '__main__':
    logging.basicConfig(filename=settings.HOME_DIR + 'proms.log',
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)s %(message)s')

    app.run(host='0.0.0.0', port=9000, threaded=True)




