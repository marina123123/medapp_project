from flask import (
    Blueprint,
    render_template,
    request
)

import config

module = Blueprint("module_results", __name__)

@module.route("/results_radiology/<survey_type>/<id>/<date>", methods=["POST", "GET"])
def results_radiology(survey_type, id, date):
    return render_template("module_newsurvey/results_radiology_footer.html",
                           survey_type = survey_type,
                           langfields = config.Config.LANGFIELDS,
                           active = "radiology",
                           id = id,
                           date = date)


@module.route("/results_dermatlogy/<survey_type>/<id>/<date>", methods=["POST", "GET"])
def results_dermatology(survey_type, id, date):
    return render_template("module_newsurvey/results_dermatology_footer.html",
                           survey_type = survey_type,
                           langfields = config.Config.LANGFIELDS,
                           active = "dermatology",
                           id = id,
                           date = date)


@module.route("/results_histology/<survey_type>/<id>/<date>", methods=["POST", "GET"])
def results_histology(survey_type, id, date):
    return render_template("module_newsurvey/results_histology_footer.html",
                           survey_type = survey_type,
                           langfields = config.Config.LANGFIELDS,
                           active = "histology",
                           id = id,
                           date = date)
