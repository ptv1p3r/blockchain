from flask import Blueprint, jsonify

dnsRoute = Blueprint('dnsRoute', __name__)


@dnsRoute.route('/helo')
def hello():
    return jsonify({'message': "Hello"})
