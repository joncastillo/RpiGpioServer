# communicates with AI Model,
from flask import Flask, request, jsonify
from emotion_analyzer import emotion_analyzer as ea
from color_lookup import color_lookup
import requests
import random

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

@app.route('/configure_lighting', methods=['POST'])
def delete_all_events():
    data = request.get_json()
    response = forward_request('configure_lighting', data)
    return jsonify(response)

@app.route('/roll_dice', methods=['POST'])
def roll_dice():
    value = random.randint(1, 6)
    return jsonify({"status": "OK", "value": value})

@app.route('/emotion_classifier', methods=['POST'])
def emotion_classifier():
    data = request.get_json()
    sentences = data.get('sentences')
    emotions = ea(sentences)
    return jsonify({"status": "OK", "emotions": emotions})

@app.route('/convert_color_from_name', methods=['POST'])
def convert_color_from_name():
    data = request.get_json()
    colorname = data.get('colorname', '').lower()
    hex_code = color_lookup.get(colorname)

    if hex_code:
        rgb = tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))
        rgbpct = tuple(round(x / 255, 3) for x in rgb)
        return jsonify({
            "status": "OK",
            "hex": hex_code,
            "rgb": f"{rgb[0]},{rgb[1]},{rgb[2]}",
            "rgbpct": f"{rgbpct[0]}, {rgbpct[1]}, {rgbpct[2]}"
        })
    else:
        return jsonify({"status": "Error", "message": "Color not found"}), 404



if __name__ == '__main__':
    app.run(debug=False)