from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/helo')
def hello():
    return jsonify({'message': "Hello"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)