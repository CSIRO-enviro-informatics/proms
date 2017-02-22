import logging
from flask import Flask
import settings
from routes import objects, pages, api
# from secure.api import api -- not implemented yet

app = Flask(__name__)

# regex paths
app.url_map.strict_slashes = True

app.register_blueprint(pages.pages)
app.register_blueprint(api.api)
app.register_blueprint(objects.modelx)
# app.register_blueprint(api) -- rename this from 'api' to secure or something

# run the app
if __name__ == '__main__':
    logging.basicConfig(
        filename=settings.LOGFILE,
        level=settings.LOG_LEVEL,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s'
    )

    # logging.log(logging.INFO, 'PROMS Started, %(host)s:%(port)d' % {'host': settings.BASE_URI, 'port': settings.PORT})

    # prod logging
    # handler = logging.FileHandler(settings.LOGFILE)
    # handler.setLevel(settings.LOG_LEVEL)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    # app.logger.addHandler(handler)

    app.run(
        threaded=True,
        debug=settings.DEBUG
    )
