from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/helo')
def hello():
    return jsonify({'message': "Hello"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, debug=True)