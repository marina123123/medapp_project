from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)
from flask_login import login_user, current_user
import config
from .models import User, Survey, db

module = Blueprint("module_auth", __name__)


@module.route("/")
@module.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("btn_enter") is not None:

            user = User.query.filter_by(username=request.form.get("input_username")).first()
            login_user(user)

            if not (user is None) and user.check_password(request.form.get("input_password")):
                return redirect(url_for("module_surveys.articles",
                                        langfields=config.Config.LANGFIELDS,
                                        active="articles",
                                        wex_image="False"))

    return render_template("module_auth/login.html",
                           lang=config.Config.LANG,
                           langfields=config.Config.LANGFIELDS)


@module.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        if request.form.get("btn_enter") is not None:
            user_exists = User.query.filter_by(username=request.form.get("input_username")).first()
            email_exists = User.query.filter_by(email=request.form.get("input_email")).first()

            if (user_exists is None) and (email_exists is None):
                user = User(spec=request.form.get("select_spec"),
                            username=request.form.get("input_username"),
                            email=request.form.get("input_email"))
                user.set_password(request.form.get("input_password"))
                db.session.add(user)
                db.session.commit()

                return redirect(url_for("module_auth.login",
                               langfields=config.Config.LANGFIELDS))

    return render_template("module_auth/registration.html",
                           lang=config.Config.LANG,
                           langfields=config.Config.LANGFIELDS)

