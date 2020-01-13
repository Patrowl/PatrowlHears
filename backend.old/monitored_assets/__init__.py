from flask import Blueprint
bp_assets = Blueprint('assets', __name__)

from . import apis
