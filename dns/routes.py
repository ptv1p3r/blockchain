from dns import app
from flask import jsonify

@app.route('/helo')
def hello():
    return jsonify({'message': "Hello"})