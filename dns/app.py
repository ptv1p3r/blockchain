import datetime
from gevent.pywsgi import WSGIServer
from flask import Flask
from dns.routes import *

app = Flask(__name__)

# Regista o endpoint dnsRoute
app.register_blueprint(dnsRoute)

ttl()


@app.route("/")
def index():
    return "ISMAT 2020 Computação Distribuida : BlockChain DNS" + ' {0:%Y-%m-%d %H:%M:%S}'.format(datetime.now())


if __name__ == '__main__':
    if SERVER_MODE_DEV:
        app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)
    else:
        http_server = WSGIServer(('0.0.0.0', SERVER_PORT), app)
        http_server.serve_forever()
