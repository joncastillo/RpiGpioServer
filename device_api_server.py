from device_hw_abstraction import Hw_Abstraction
from flask import Flask, request, jsonify
from lifx_lighting_controller import Lifx_Lighting_Controller

app = Flask(__name__)

@app.route('/initialize_gpio_pins', methods=['POST'])
def initialize_gpio_pins_route():
    data = request.get_json()
    gpio_pins = data.get('gpio_pins')
    result = hwAbstraction.initialize_gpio_pins(gpio_pins)
    return jsonify(result)

@app.route('/set_triggered_events', methods=['POST'])
def set_triggered_events_route():
    data = request.get_json()
    triggered_events = data.get('triggered_events')
    result = hwAbstraction.set_triggered_events(triggered_events)
    return jsonify(result)

@app.route('/set_timed_events', methods=['POST'])
def set_timed_events_route():
    data = request.get_json()
    triggered_events = data.get('triggered_events')
    result = hwAbstraction.set_timed_events(triggered_events)
    return jsonify(result)

@app.route('/trigger_immediate_event', methods=['POST'])
def trigger_immediate_event_route():
    data = request.get_json()
    triggered_events = data.get('triggered_events')
    result = hwAbstraction.trigger_immediate_event(triggered_events)
    return jsonify(result)

@app.route('/delete_events', methods=['POST'])
def delete_events():
    data = request.get_json()
    events = data.get('events')
    response = hwAbstraction.delete_events(events)
    return jsonify(response)

@app.route('/delete_all_events', methods=['POST'])
def delete_all_events():
    data = request.get_json()
    response = hwAbstraction.delete_all_events()
    return jsonify(response)

@app.route('/configure_lighting', methods=['POST'])
def configure_lighting():
    data = request.get_json()
    response = lifx_lightning_controller.configure_lighting(data.get('lighting_list'))
    return jsonify(response)


if __name__ == '__main__':
    hwAbstraction = Hw_Abstraction()
    lifx_lightning_controller = Lifx_Lighting_Controller
    app.run(debug=True, host='0.0.0.0')