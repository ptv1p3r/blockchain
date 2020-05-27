from flask import Flask
from dns import routes
from dns.config import *

app = Flask(__name__)



if SERVER_MODE_DEV:
    if __name__ == '__main__':
        app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)
