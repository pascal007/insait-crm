from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from flask_swagger_ui import get_swaggerui_blueprint

from routes.routes import initialize_routes

load_dotenv()


def create_app():
    flask_app = Flask(__name__)
    api = Api(flask_app)
    initialize_routes(api)

    SWAGGER_URL = "/swagger"
    API_URL = "/static/swagger.json"

    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'Insait API'
        }
    )
    flask_app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    return flask_app


if __name__ == '__main__':
    app = create_app()

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)
