import os
from flask import Flask
from .database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])

    db.init_app(app)
    with app.test_request_context():
        db.create_all()

    import app.module_auth.controllers as module_auth

    app.register_blueprint(module_auth.module)

    return app
