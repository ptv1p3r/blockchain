from flask import Flask, jsonify
from dns.config import *

app = Flask(__name__)


@app.route('/helo')
def hello():
    return jsonify({'message': "Hello"})


if SERVER_MODE_DEV:
    if __name__ == '__main__':
        app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)
