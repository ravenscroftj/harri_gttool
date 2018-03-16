from flask import Flask, send_from_directory
from .model import db, User, Role

from flask_security import Security, SQLAlchemyUserDatastore

# Setup Flask-Security
security = Security()


def create_app():
    """Create app """
    app = Flask(__name__)

    # set up configuration
    app.config.from_object(__name__ + '.config.default_settings')
    app.config.from_envvar('FLASK_SETTINGS')
    app.config['DEBUG'] = True

    # special route for app media (compiled JS)
    @app.route('/media/<path:filename>')
    def send_media(filename):
        return send_from_directory(app.config['STATIC_FOLDER'], filename)

    # register routes and modules
    from .views import app_views
    from .resources import api_bp


    app.register_blueprint(app_views)
    app.register_blueprint(api_bp)

    # register database
    db.init_app(app)

    #register security
    datastore =  SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, datastore)

    return app


def main():
    """Main entrypoint for handling server"""

    app = create_app()

    import argparse

    argparser = argparse.ArgumentParser()

    argparser.add_argument("--host", dest="host", default="127.0.0.1",
                           help="Host IP to bind to (default 127.0.0.1)")

    argparser.add_argument("--port", "-p", type=int, dest="port", default=5000,
                           help="Port to bind to (default 5000)")

    argparser.add_argument("-d", "--debug", dest="debug", type=bool,
                           default=False,
                           help="Enable debug mode (default False)")

    args = argparser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)


# add handler for this file being run as a script
if __name__ == "__main__":
    main()
