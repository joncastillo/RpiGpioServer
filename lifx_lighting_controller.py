import pigpio
import requests
import time
import os
from color_lookup import color_lookup
class Lifx_Lighting_Controller:
    reserved_pin_map = {
        "INPUT_1": { 'gpio_number': 2, 'pin_type': 'INPUT'},
        "INPUT_2": { 'gpio_number': 4, 'pin_type': 'INPUT'},
        "INPUT_3": { 'gpio_number': 5, 'pin_type': 'INPUT'},
        "INPUT_4": { 'gpio_number': 6, 'pin_type': 'INPUT'},
        "INPUT_5": { 'gpio_number': 7, 'pin_type': 'INPUT'},
    }

    lighting_colors = {
        "00000": { 'color': "000000", 'brightness': 0.5 },
        "00001": { 'color': "000000", 'brightness': 0.5 },
        "00010": { 'color': "000000", 'brightness': 0.5 },
        "00011": { 'color': "000000", 'brightness': 0.5 },
        "00100": { 'color': "000000", 'brightness': 0.5 },
        "00101": { 'color': "000000", 'brightness': 0.5 },
        "00110": { 'color': "000000", 'brightness': 0.5 },
        "00111": { 'color': "000000", 'brightness': 0.5 },
        "01000": { 'color': "000000", 'brightness': 0.5 },
        "01001": { 'color': "000000", 'brightness': 0.5 },
        "01010": { 'color': "000000", 'brightness': 0.5 },
        "01011": { 'color': "000000", 'brightness': 0.5 },
        "01100": { 'color': "000000", 'brightness': 0.5 },
        "01101": { 'color': "000000", 'brightness': 0.5 },
        "01110": { 'color': "000000", 'brightness': 0.5 },
        "01111": { 'color': "000000", 'brightness': 0.5 },
        "10000": { 'color': "000000", 'brightness': 0.5 },
        "10001": { 'color': "000000", 'brightness': 0.5 },
        "10010": { 'color': "000000", 'brightness': 0.5 },
        "10011": { 'color': "000000", 'brightness': 0.5 },
        "10100": { 'color': "000000", 'brightness': 0.5 },
        "10101": { 'color': "000000", 'brightness': 0.5 },
        "10110": { 'color': "000000", 'brightness': 0.5 },
        "10111": { 'color': "000000", 'brightness': 0.5 },
        "11000": { 'color': "000000", 'brightness': 0.5 },
        "11001": { 'color': "000000", 'brightness': 0.5 },
        "11010": { 'color': "000000", 'brightness': 0.5 },
        "11011": { 'color': "000000", 'brightness': 0.5 },
        "11100": { 'color': "000000", 'brightness': 0.5 },
        "11101": { 'color': "000000", 'brightness': 0.5 },
        "11110": { 'color': "000000", 'brightness': 0.5 },
        "11111": { 'color': "000000", 'brightness': 0.5 }
    }

    def __init__(self):
        self.pi = pigpio.pi()
        self.initialize_gpio()
        self.last_trigger_time = time.time()

    def initialize_gpio(self):
        self.last_trigger_time = time.time()  # Track the last time the callback was triggered

        def input_change_callback(gpio, level, tick):
            current_time = time.time()
            if current_time - self.last_trigger_time < 0.2:  # Debounce interval of 200ms
                return
            self.last_trigger_time = current_time
            time.sleep(1)


            input_1_state = self.pi.read(self.reserved_pin_map["INPUT_1"]["gpio_number"])
            input_2_state = self.pi.read(self.reserved_pin_map["INPUT_2"]["gpio_number"])
            input_3_state = self.pi.read(self.reserved_pin_map["INPUT_3"]["gpio_number"])
            input_4_state = self.pi.read(self.reserved_pin_map["INPUT_4"]["gpio_number"])
            input_5_state = self.pi.read(self.reserved_pin_map["INPUT_5"]["gpio_number"])

            input_bitfield = f"{input_1_state}{input_2_state}{input_3_state}{input_4_state}{input_5_state}"
            lighting_color = self.lighting_colors[input_bitfield]["color"]
            lighting_brightness = self.lighting_colors[input_bitfield]["brightness"]

            api_key = os.getenv("LIFX_API_KEY")
            headers = {
                "Authorization": "Bearer " + api_key
            }
            url = "https://api.lifx.com/v1/lights/all/state"  # Replace with your endpoint URL

            data = {
                "power": "on",
                "color": lighting_color,
                "brightness": lighting_brightness,
                "duration": 1
            }

            try:
                print(f"sending {input_bitfield}: {data}")
                response = requests.put(url, json=data, headers=headers)
                response.raise_for_status()  # Raises an error for HTTP error codes
                print(f"received: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")


        for gpio_label, gpio_info in self.reserved_pin_map.items():
            gpio_number = gpio_info['gpio_number']
            pin_type = gpio_info['pin_type'].lower()

            if pin_type.lower() == 'input':
                self.pi.set_mode(gpio_number, pigpio.INPUT)
                self.pi.set_pull_up_down(gpio_number, pigpio.PUD_DOWN)
                self.pi.callback(gpio_number, pigpio.EITHER_EDGE, input_change_callback)

    def set_lighting(self, lighting_list):
        # check first for input errors:
        for lighting in lighting_list:
            bitmask = lighting["bitmask"]
            if len(bitmask) != len(self.reserved_pin_map) :
                raise ValueError(f"ERROR, Invalid bitmask: {bitmask}.")
            if not all(char in '01' for char in bitmask):
                raise ValueError(f"ERROR, Invalid bitmask: {bitmask}.")

            lighting_color = lighting["color"]
            if len(lighting_color) != 6 :
                raise ValueError(f"ERROR, Invalid lighting color: {lighting_color}.")
            if not all(char in '0123456789ABCDEF' for char in lighting_color):
                raise ValueError(f"ERROR, Invalid lighting_color: {lighting_color}.")

        for lighting in lighting_list:
            bitmask = lighting["bitmask"]
            lighting_color = lighting["color"]
            try:
                lighting_brightness = float(lighting["brightness"])
            except (ValueError, TypeError):
                lighting_brightness = 0.0

            controller.lighting_colors[bitmask] = {'color': {lighting_color}, 'brightness': {lighting_brightness}}

if __name__ == "__main__":
    # tests, store LIFX key in LIFX_API_KEY
    pi = pigpio.pi()
    controller = Lifx_Lighting_Controller()
    controller.lighting_colors["00000"] = { 'color': color_lookup["terracotta"], 'brightness': 0.1 }
    controller.lighting_colors["10000"] = { 'color': color_lookup["tiffany blue"], 'brightness': 0.1 }
    gpio_number = controller.reserved_pin_map["INPUT_1"]["gpio_number"]

    #pi.set_mode(gpio_number, pigpio.OUTPUT)
    print("Testing: Toggling GPIO to trigger callback")
    for _ in range(5):
       pi.write(gpio_number, 1)
       time.sleep(4)
       pi.write(gpio_number, 0)
       time.sleep(4)

