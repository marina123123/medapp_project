from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)
import config
import os
from werkzeug import secure_filename
import time
import json
import app.image_processing_NEW as im_p
import numpy as np
import app.mri_txt as mri_txt
from app.module_auth.models import User, Survey, db
from flask_login import current_user, login_required
from flask_weasyprint import HTML

module = Blueprint("module_newsurvey", __name__)


def save_file(path_for_analysis, request):
    file = request.files["file_for_analysis"]
    filename = secure_filename(file.filename)

    if not os.path.exists(path_for_analysis):
        os.makedirs(path_for_analysis)

    file.save(os.path.join(path_for_analysis, filename))

    return filename


def get_metainfo(path):
    with open(path, "r") as f:
        colnames = f.readline()
        colnames = colnames.replace("\n", "").replace("\s", "").replace("r", "")
        colnames = colnames.split(",")

        values = f.readlines()
        values = [v.replace("\n", "").replace("\s", "").replace("r", "").split(",") for v in values]

        return colnames, values


def create_survey(username, unique_id, date, rid, location, type, survey, pdf):
    survey = Survey(username=username,
                    unique_id=unique_id,
                    date=date,
                    rid=rid,
                    location=location,
                    type=type,
                    survey=survey,
                    pdf=pdf)

    db.session.add(survey)
    db.session.commit()


def write_read_pdf_report(html, path_for_pdf):
    pdf = HTML(string=html).write_pdf(path_for_pdf)
    with open(path_for_pdf, 'rb') as pdf_file:
        pdf_file = pdf_file.read()

    return pdf_file


@module.route("/newsurvey_radiology/<survey_type>/<id>/<date>", methods=["POST", "GET"])
@login_required
def newsurvey_radiology(survey_type, id, date):
    if request.method == "POST":
        if request.form.get("btn_analyse") is not None:
            id = id
            rid = request.form.get("input_rid")
            date = date
            method = survey_type
            path_for_analysis = os.path.join(config.Config.UPLOAD_FOLDER,
                                             id,
                                             "Input")
            path_for_output = os.path.join(config.Config.UPLOAD_FOLDER,
                                           id,
                                           "Output")

            filename = save_file(path_for_analysis, request)
            start = time.time()
            im_p.image_processing_MRI(id, method)
            end = time.time()
            print(end - start)

            colnames, values = get_metainfo(os.path.join(path_for_output, "results.csv"))

            dirnames = list(filter(lambda x: os.path.isdir(os.path.join(path_for_output, x)),
                                   os.listdir(path_for_output)))
            contr_proj = [dn.split('_') for dn in dirnames]
            files_in_dirs = []
            for dn in dirnames:
                f_in_dn = os.listdir(os.path.join(path_for_output, dn))
                fp_f_in_dn = [os.path.join(path_for_output.split("static/")[1], dn, f) for f in
                              os.listdir(os.path.join(path_for_output, dn))]
                files_in_dirs.append(dict(zip(f_in_dn, fp_f_in_dn)))

            selected_name = []
            selected_path = []
            for i, dn in enumerate(dirnames):
                if list(files_in_dirs[i].keys()) != []:
                    selected_name.append(list(files_in_dirs[i].keys())[0])
                    selected_path.append(list(files_in_dirs[i].values())[0])
                else:
                    selected_name.append("- no images -")
                    selected_path.append("")


            html = render_template("module_results/pdf.html",
                                   id=id,
                                   rid=rid,
                                   date=date,
                                   survey_type=survey_type,
                                   colnames=colnames,
                                   values=values,
                                   data=zip(contr_proj, files_in_dirs),
                                   selected_name=selected_name,
                                   selected_path=selected_path,
                                   langfields=config.Config.LANGFIELDS,
                                   active="radiology")

            pdf_file = write_read_pdf_report(html, os.path.join(path_for_output, id + ".pdf"))

            create_survey(username=current_user.username,
                          unique_id=id,
                          date=date,
                          rid=rid,
                          location=request.form.get("select_loc"),
                          type=method,
                          survey="Radiology",
                          pdf=pdf_file)

            return render_template("module_results/results_radiology_footer.html",
                                   id=id,
                                   rid=rid,
                                   date=date,
                                   survey_type=survey_type,
                                   colnames=colnames,
                                   values=values,
                                   data=zip(contr_proj, files_in_dirs),
                                   selected_name=selected_name,
                                   selected_path=selected_path,
                                   langfields=config.Config.LANGFIELDS,
                                   active="radiology")


    return render_template("module_newsurvey/newsurvey_footer.html",
                           survey_type=survey_type,
                           locs=config.Config.SURVEYS["Radiology"][survey_type.replace(" ", "_")]["locs"],
                           langfields=config.Config.LANGFIELDS,
                           active="radiology",
                           id=id,
                           date=date)


@module.route("/newsurvey_dermatology/<survey_type>/<id>/<date>", methods=["POST", "GET"])
@login_required
def newsurvey_dermatology(survey_type, id, date):
    if request.method == "POST":
        if request.form.get("btn_analyse") is not None:
            id = id
            rid = request.form.get("input_rid")
            date = date
            method = survey_type
            path_for_analysis = os.path.join(config.Config.UPLOAD_FOLDER,
                                             id,
                                             "Input")
            path_for_output = os.path.join(config.Config.UPLOAD_FOLDER,
                                           id,
                                           "Output")

            filename = save_file(path_for_analysis, request)
            start = time.time()
            im_p.image_processing_Dermatoscopy(id, method)
            end = time.time()
            print(end - start)

            colnames, values = get_metainfo(os.path.join(path_for_output, "results.csv"))
            colnames = ["", "Accuracy (image analysis)"]

            fls = [f for f in os.listdir(path_for_output) if not f.endswith(".csv")]
            path = os.path.join(path_for_output.split("static/")[1], fls[0])

            with open(config.Config.PATH_DERM_DISEASES, "r+", encoding="utf-8") as json_file:
                derm_diseases = json.load(json_file)
            cur_disease = {"locs": [request.form.get("select_loc")],
                           "sex": [request.form.get("sex")],
                           "age": [request.form.get("age")],
                           "skin phototype": [request.form.get("skin")],
                           "family history": [request.form.get("family")],
                           "'prolonged sun exposure": [request.form.get("prolonged")],
                           "injury": [request.form.get("injury")],
                           "lesions": [request.form.get("lesions")],
                           "color": [request.form.get("color")],
                           "desquamation": [request.form.get("desquamation")],
                           "number": [request.form.get("number")]}

            percents = dict(zip(derm_diseases.keys(), np.zeros(len(derm_diseases.keys()))))
            for disease, vals in derm_diseases.items():
                inter = []

                for v in cur_disease.values():
                    if v[0] in sum(list(vals.values()), []):
                        inter.append(v[0])

                percents[disease] = len(inter)

            all_vals = sum(list(percents.values()))

            for k, v in percents.items():
                percents[k] = np.round(percents[k] / all_vals, 2) if all_vals != 0 else percents[k]

            colnames_text = ["", "Accuracy (anamnesis analysis)"]
            values_text = [[k.replace("_", " "), v] for k, v in percents.items()]

            html = render_template("module_results/pdf.html",
                                   id=id,
                                   rid=rid,
                                   date=date,
                                   survey_type=survey_type,
                                   colnames=colnames,
                                   values=values,
                                   colnames_text=colnames_text,
                                   values_text=values_text,
                                   path=path,
                                   langfields=config.Config.LANGFIELDS,
                                   active="dermatology")

            pdf_file = write_read_pdf_report(html, os.path.join(path_for_output, id + ".pdf"))

            create_survey(username=current_user.username,
                          unique_id=id,
                          date=date,
                          rid=rid,
                          location=request.form.get("select_loc"),
                          type=method,
                          survey="Dermatology",
                          pdf=pdf_file)

            return render_template("module_results/results_dermatology_footer.html",
                                   id=id,
                                   rid=rid,
                                   date=date,
                                   survey_type=survey_type,
                                   colnames=colnames,
                                   values=values,
                                   colnames_text=colnames_text,
                                   values_text=values_text,
                                   path=path,
                                   langfields=config.Config.LANGFIELDS,
                                   active="dermatology")

    return render_template("module_newsurvey/newsurvey_dermatology.html",
                           survey_type=survey_type,
                           locs=config.Config.SURVEYS["Dermatology"][survey_type.replace(" ", "_")]["locs"],
                           text_fields=config.Config.SURVEYS["Dermatology"][survey_type.replace(" ", "_")][
                               "text_fields"],
                           langfields=config.Config.LANGFIELDS,
                           active="dermatology",
                           id=id,
                           date=date)


@module.route("/newsurvey_histology/<survey_type>/<id>/<date>", methods=["POST", "GET"])
@login_required
def newsurvey_histology(survey_type, id, date):
    if request.method == "POST":
        if request.form.get("btn_analyse") is not None:
            id = id
            rid = request.form.get("input_rid")
            date = date
            method = survey_type
            path_for_analysis = os.path.join(config.Config.UPLOAD_FOLDER,
                                             id,
                                             "Input")
            path_for_output = os.path.join(config.Config.UPLOAD_FOLDER,
                                           id,
                                           "Output")

            filename = save_file(path_for_analysis, request)
            start = time.time()
            im_p.image_processing_Histology(id, method)
            end = time.time()
            print(end - start)

            colnames, values = get_metainfo(os.path.join(path_for_output, "results.csv"))

            dirnames = [""]

            files_in_dirs = []
            for dn in dirnames:
                f_in_dn = os.listdir(os.path.join(path_for_output, dn))
                fp_f_in_dn = [os.path.join(path_for_output.split("static/")[1], dn, f) for f in
                              os.listdir(os.path.join(path_for_output, dn))]
                files_in_dirs.append(dict(zip(f_in_dn, fp_f_in_dn)))

            selected_name = []
            selected_path = []
            for i, dn in enumerate(dirnames):
                if list(files_in_dirs[i].keys()) != []:
                    selected_name.append(list(files_in_dirs[i].keys())[0])
                    selected_path.append(list(files_in_dirs[i].values())[0])
                else:
                    selected_name.append("- no images -")
                    selected_path.append("")

            html = render_template("module_results/pdf.html",
                                   id=id,
                                   rid=rid,
                                   date=date,
                                   survey_type=survey_type,
                                   colnames=colnames,
                                   values=values,
                                   data=files_in_dirs,
                                   selected_name=selected_name,
                                   selected_path=selected_path,
                                   langfields=config.Config.LANGFIELDS,
                                   active="histology")

            pdf_file = write_read_pdf_report(html, os.path.join(path_for_output, id + ".pdf"))

            create_survey(username=current_user.username,
                          unique_id=id,
                          date=date,
                          rid=rid,
                          location=request.form.get("select_loc"),
                          type=method,
                          survey="Histology",
                          pdf=pdf_file)

            return render_template("module_results/results_histology_footer.html",
                                   id=id,
                                   rid=rid,
                                   date=date,
                                   survey_type=survey_type,
                                   colnames=colnames,
                                   values=values,
                                   data=files_in_dirs,
                                   selected_name=selected_name,
                                   selected_path=selected_path,
                                   langfields=config.Config.LANGFIELDS,
                                   active="histology")

    return render_template("module_newsurvey/newsurvey_footer.html",
                           survey_type=survey_type,
                           locs=config.Config.SURVEYS["Histology"][survey_type.replace(" ", "_")]["locs"],
                           langfields=config.Config.LANGFIELDS,
                           active="histology",
                           id=id,
                           date=date)


@module.route("/newsurvey_protocols/<survey_type>/<id>/<date>", methods=["POST", "GET"])
@login_required
def newsurvey_protocols(survey_type, id, date):
    if request.method == "POST":
        if request.form.get("btn_analyse") is not None:
            id = id
            rid = request.form.get("input_rid")
            date = date
            method = survey_type
            path_for_analysis = os.path.join(config.Config.UPLOAD_FOLDER,
                                             id,
                                             "Input")
            path_for_output = os.path.join(config.Config.UPLOAD_FOLDER,
                                           id,
                                           "Output")

            filename = save_file(path_for_analysis, request)

            with open(os.path.join(path_for_analysis, filename), 'r') as f:
                textfromfile = f.readlines()

            outstrings, checks = mri_txt.mri_text(os.path.join(path_for_analysis, filename))

            html = render_template("module_results/pdf.html",
                                   id=id,
                                   rid=rid,
                                   method=method,
                                   date=date,
                                   langfields=config.Config.LANGFIELDS,
                                   textfromfile=textfromfile,
                                   outstrings=outstrings,
                                   checks=checks,
                                   active="protocols")

            pdf_file = write_read_pdf_report(html, os.path.join(path_for_analysis, id + ".pdf"))

            create_survey(username=current_user.username,
                          unique_id=id,
                          date=date,
                          rid=rid,
                          location=request.form.get("select_loc"),
                          type=method,
                          survey="Protocols",
                          pdf=pdf_file)

            return render_template("module_results/results_protocols_footer.html",
                                   id=id,
                                   rid=rid,
                                   method=method,
                                   date=date,
                                   langfields=config.Config.LANGFIELDS,
                                   textfromfile=textfromfile,
                                   outstrings=outstrings,
                                   checks=checks,
                                   active="protocols")

    return render_template("module_newsurvey/newsurvey_footer.html",
                           survey_type=survey_type,
                           locs=config.Config.SURVEYS["Protocols"][survey_type.replace(" ", "_")]["locs"],
                           langfields=config.Config.LANGFIELDS,
                           active="protocols",
                           id=id,
                           date=date)