import datetime, sys, os
from wsgiref.simple_server import WSGIServer

from flask import Flask
from dns.config import *
from dns.routes import *

app = Flask(__name__)
# Regista o endpoint dnsRoute
app.register_blueprint(dnsRoute)


# Aviso no IP 127.0.0.1
@app.route("/")
def index():
    return "Computação Distribuida : BlockChain" + ' {0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())


if __name__ == '__main__':
    if SERVER_MODE_DEV:
        app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)
    else:
        http_server = WSGIServer(('', SERVER_PORT), app)
        http_server.serve_forever()
