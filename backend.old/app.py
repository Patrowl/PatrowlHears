from flask import Flask, jsonify
from flask_cors import CORS
from flask_mongoengine import MongoEngine

# configuration
DEBUG = True

app = Flask(__name__)
# app = Flask(__name__, instance_relative_config=False)
# Application Configuration
app.config.from_object(__name__)
# app.config.from_object('config.Config')
app.config['MONGODB_SETTINGS'] = {
    "db": "hears",
}

db = MongoEngine(app)

CORS(app, resources={r'/*': {'origins': '*'}})


with app.app_context():
    from monitored_assets import bp_assets
    app.register_blueprint(bp_assets, url_prefix='/api/assets')


@app.route('/health', methods=['GET'])
def health():
    return jsonify('OK')


if __name__ == '__main__':
    app.run(port=3333)
