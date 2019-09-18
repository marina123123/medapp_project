from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    abort,
    redirect,
    url_for,
    current_app,
)
from sqlalchemy.exc import SQLAlchemyError

# from .models import Entity, db
# from .forms import EntityCreateForm
# from app.comment.models import Comment

module = Blueprint('module_auth', __name__)

@module.route('/', methods=['GET'])
def index():
    return render_template('module_auth/index.html')