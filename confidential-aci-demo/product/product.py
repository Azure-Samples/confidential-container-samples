from flask import Flask, jsonify, request
import requests
app = Flask(__name__)


@app.route('/product', methods=['POST'])
def calculate_product():
    # retrieve the two numbers from the request
    data = request.get_json()
    num1 = data['num1']
    num2 = data['num2']

    # calculate the product of the two numbers
    result = num1 * num2

    # return the result as a JSON object
    return jsonify({'result': result})


@app.route('/attest/maa', methods=['POST'])
def attest_maa():
    # retrieve the two numbers from the request
    data = request.get_json()
    maa_endpoint = data['maa_endpoint']
    runtime_data = data['runtime_data']

    response = requests.post("http://localhost:8080/attest/maa",
                             json={"maa_endpoint": maa_endpoint, "runtime_data": runtime_data})

    # return the result as a JSON object
    return jsonify({'result': response.text})


@app.route('/attest', methods=['POST'])
def attest():
    # retrieve the two numbers from the request
    data = request.get_json()
    runtime_data = data['runtime_data']

    response = requests.post("http://localhost:8080/attest/raw",
                             json={"runtime_data": runtime_data})

    # return the result as a JSON object
    return jsonify({'result': response.text})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
