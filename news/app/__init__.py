from typing import List, Tuple
from flask import Flask, Blueprint
from flask_cors import CORS

from app.config import Blueprints, Config, RequestLoggerMiddleware
from app.initializer import db, migrate

# from .apis import register as api_register
from .routers import register as view_register

routes: List[Tuple[List[Blueprint], str]] = [  # Routes and prefix
    # (api_register, "/api"),
    (view_register, "/"),
]


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.wsgi_app = RequestLoggerMiddleware(app.wsgi_app)

    with app.app_context():
        print(routes)
        blue_print = Blueprints(app, routes)
        blue_print.register_blueprint()

    return app
