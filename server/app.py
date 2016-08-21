from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/heartbeat')
def heartbeat():
    freezer_temp = { 'temp': '18C' }
    return jsonify(**freezer_temp)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


