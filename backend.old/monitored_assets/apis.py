from flask import jsonify, request
from flask import current_app as app
from flask_mongoengine import MongoEngine
from . import bp_assets as bp
from app import db
from .models import MonitoredAsset

@bp.route("/")
def index():
    # print(dir(app))

    # print(app.__dict__)
    # print(app._get_current_object())
    # print(app.extensions['mongoengine'])
    return "Hello Assets!"


@bp.route("/list")
def list_assets():
    return jsonify("1")


@bp.route("/add", methods=['GET', 'POST', 'PUT'])
def add_asset():
    asset_name = ""
    asset_type = ""
    if request.method == 'GET':
        asset_name = request.args.get('name')
        asset_type = request.args.get('type')
    elif request.method in ['POST', 'PUT']:
        asset_name = request.form.get('name')
        asset_type = request.form.get('type')

    print(asset_type, asset_name)

    return jsonify("1")
