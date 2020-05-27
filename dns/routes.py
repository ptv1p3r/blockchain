from dns import app
from flask import jsonify


@app.route('/hello')
def hello():
    return jsonify({'message': "Hello"})
