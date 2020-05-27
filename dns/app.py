from flask import Flask, jsonify
from dns.config import *
from dns.routes import *

app = Flask(__name__)
# Regista o endpoint dnsRoute
app.register_blueprint(dnsRoute)

if SERVER_MODE_DEV:
    if __name__ == '__main__':
        app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)
