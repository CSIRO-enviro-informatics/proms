import logging
import settings
from flask import Flask
from routes import routes
app = Flask(__name__)


#import the routes in routes.py
app.register_blueprint(routes)


#run the app
if __name__ == '__main__':
    logging.basicConfig(filename=settings.HOME_DIR + 'proms.log',
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)s %(message)s')

    app.run(host='0.0.0.0', port=9000)

