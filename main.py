from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv

from routes.routes import initialize_routes

load_dotenv()


def create_app():
    flask_app = Flask(__name__)
    api = Api(flask_app)
    initialize_routes(api)
    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)
