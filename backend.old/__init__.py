from flask import Flask, jsonify
from flask_cors import CORS
from flask_mongoengine import MongoEngine

from .monitored_asset import bp as ma_bp


# Configuration
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/hears"
app.config['MONGODB_SETTINGS'] = {
    "db": "hears",
}

db = MongoEngine(app)

CORS(app, resources={r'/*': {'origins': '*'}})

# Register Blueprints
app.register_blueprint(ma_bp, url_prefix='/api/assets')
