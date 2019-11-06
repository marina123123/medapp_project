from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    url_for
)
from flask import send_file
from flask_login import current_user
from app.module_auth.models import User, Survey, db
import config
import app.wex_search as wex_search
import datetime
import uuid
from io import BytesIO


module = Blueprint("module_surveys", __name__)


def generate_id():
    date_today = datetime.date.today()
    unique_id = uuid.uuid4()
    unique_id = str(unique_id)

    return date_today, unique_id


@module.route("/articles", methods=["GET", "POST"])
def articles():
    if request.method == "POST":
        print(request.form.get("btn_search"))

        if request.form.get("btn_search") is not None:
            input_search = request.form.get("input_search")
            links = wex_search.wex_search(request.form.get("input_search"))

            return render_template("module_surveys/articles.html",
                                   active="articles",
                                   wex_image="True",
                                   links=links,
                                   input_search=input_search,
                                   langfields = config.Config.LANGFIELDS)

    return render_template("module_surveys/articles.html",
                           langfields = config.Config.LANGFIELDS,
                           active = "articles",
                           wex_image = "False")


@module.route("/radiology", methods=["GET", "POST"])
def radiology():
    history = Survey.query.filter_by(username=current_user.username, survey="Radiology").all()

    if request.method == "POST":
        if request.form.get("btn_new") is not None:
            date, id = generate_id()
            survey_type = request.form.get("select_researchtype").replace(" ", "_")

            return redirect(url_for("module_newsurvey.newsurvey_radiology",
                                    survey_type=survey_type,
                                    locs=config.Config.SURVEYS["Radiology"][survey_type]["locs"],
                                    langfields=config.Config.LANGFIELDS,
                                    date=date,
                                    id=id))

    return render_template("module_surveys/survey.html",
                           langfields = config.Config.LANGFIELDS,
                           surveys = config.Config.SURVEYS["Radiology"],
                           active = "radiology",
                           history=history)


@module.route("/dermatology", methods=["GET", "POST"])
def dermatology():
    history = Survey.query.filter_by(username=current_user.username, survey="Dermatology").all()

    if request.method == "POST":
        if request.form.get("btn_new") is not None:
            date, id = generate_id()
            survey_type = request.form.get("select_researchtype").replace(" ", "_")

            return redirect(url_for("module_newsurvey.newsurvey_dermatology",
                                    survey_type=survey_type,
                                    locs=config.Config.SURVEYS["Dermatology"][survey_type]["locs"],
                                    langfields=config.Config.LANGFIELDS,
                                    date=date,
                                    id=id))

    return render_template("module_surveys/survey.html",
                           langfields = config.Config.LANGFIELDS,
                           surveys=config.Config.SURVEYS["Dermatology"],
                           active = "dermatology",
                           history=history)


@module.route("/histology", methods=["GET", "POST"])
def histology():
    history = Survey.query.filter_by(username=current_user.username, survey="Histology").all()

    if request.method == "POST":
        if request.form.get("btn_new") is not None:
            date, id = generate_id()
            survey_type = request.form.get("select_researchtype").replace(" ", "_")

            return redirect(url_for("module_newsurvey.newsurvey_histology",
                                    survey_type=survey_type,
                                    locs=config.Config.SURVEYS["Histology"][survey_type]["locs"],
                                    langfields=config.Config.LANGFIELDS,
                                    date=date,
                                    id=id))

    return render_template("module_surveys/survey.html",
                           langfields = config.Config.LANGFIELDS,
                           surveys=config.Config.SURVEYS["Histology"],
                           active = "histology",
                           history=history)


@module.route("/protocols", methods=["GET", "POST"])
def protocols():
    history = Survey.query.filter_by(username=current_user.username, survey="Protocols").all()

    if request.method == "POST":
        if request.form.get("btn_new") is not None:
            date, id = generate_id()
            survey_type = request.form.get("select_researchtype").replace(" ", "_")

            return redirect(url_for("module_newsurvey.newsurvey_protocols",
                                    survey_type=survey_type,
                                    locs=config.Config.SURVEYS["Protocols"][survey_type]["locs"],
                                    langfields=config.Config.LANGFIELDS,
                                    date=date,
                                    id=id))

    return render_template("module_surveys/survey.html",
                           langfields = config.Config.LANGFIELDS,
                           surveys=config.Config.SURVEYS["Protocols"],
                           active = "protocols",
                           history=history)


@module.route("/<active>/delete_from_db/<id>", methods=["POST", "GET"])
def delete_from_db(active, id):
    db.session.query(Survey).filter(Survey.unique_id==id).delete()
    db.session.commit()

    return redirect(url_for("module_surveys." + active))


@module.route("/download_pdf/<id>", methods=["POST", "GET"])
def download_pdf(id):
    row = db.session.query(Survey).filter(Survey.unique_id==id).first()

    return send_file(BytesIO(row.pdf), attachment_filename=id+".pdf", as_attachment=True)