# communicates with AI Model,
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def forward_request(endpoint, data):
    device_ip_address = data.get('device_ip_address')
    url = f'http://{device_ip_address}/{endpoint}'
    response = requests.post(url, json=data)
    print(url)
    print(response)
    return response.json()

@app.route('/initialize_gpio_pins', methods=['POST'])
def initialize_gpio_pins():
    data = request.get_json()
    response = forward_request('initialize_gpio_pins', data)
    return jsonify(response)

@app.route('/set_triggered_events', methods=['POST'])
def set_triggered_events():
    data = request.get_json()
    response = forward_request('set_triggered_events', data)
    return jsonify(response)

@app.route('/set_timed_events', methods=['POST'])
def set_timed_events():
    data = request.get_json()
    response = forward_request('set_timed_events', data)
    return jsonify(response)

@app.route('/trigger_immediate_event', methods=['POST'])
def trigger_immediate_event():
    data = request.get_json()
    response = forward_request('trigger_immediate_event', data)
    return jsonify(response)

@app.route('/delete_events', methods=['POST'])
def delete_events():
    data = request.get_json()
    response = forward_request('delete_events', data)
    return jsonify(response)

@app.route('/delete_all_events', methods=['POST'])
def delete_all_events():
    data = request.get_json()
    response = forward_request('delete_all_events', data)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=False)