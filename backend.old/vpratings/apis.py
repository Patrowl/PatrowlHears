from backend import app

@app.route('/test', methods=['GET'])
def test():
    return jsonify('test')
