import flask
from flask import Blueprint


bp = Blueprint("pages", __name__)


@bp.route("/")
def index():
    return flask.render_template("index.html")
