import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from .database import db
from app.module_auth.models import User


def create_app():
    app = Flask(__name__)
    Bootstrap(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "users.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()

    app.config.from_object(os.environ['APP_SETTINGS'])
    db.init_app(app)

    import app.module_auth.controllers as module_auth
    import app.module_surveys.controllers as module_surveys
    import app.module_newsurvey.controllers as module_newsurvey
    import app.module_results.controllers as module_results

    app.register_blueprint(module_auth.module)
    app.register_blueprint(module_surveys.module)
    app.register_blueprint(module_newsurvey.module)
    app.register_blueprint(module_results.module)

    with app.test_request_context():
        db.create_all()

    return app
