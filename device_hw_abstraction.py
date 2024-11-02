import os
import json
import ssl
import time
import threading
import pigpio
import jwt
import numpy as np
import simpleaudio as sa
from pydub import AudioSegment
from pydub.playback import play
from dateutil import parser
from datetime import datetime, timedelta, timezone

class Hw_Abstraction:
    def __init__(self):
        self.pi = pigpio.pi()
        self.pin_map = {}
        self.timed_events = []
        self.event_callbacks = {}

    def initialize_gpio_pins(self, gpio_pins):
        self.pin_map = {}
        for pin_config in gpio_pins:
            gpio_name = pin_config['gpio_name']
            pin_number = pin_config['pin_number']
            pin_type = pin_config['pin_type']

            if pin_type.lower() == 'input':
                self.pi.set_mode(pin_number, pigpio.INPUT)
            elif pin_type.lower() == 'output':
                self.pi.set_mode(pin_number, pigpio.OUTPUT)
            elif pin_type.lower() == 'pwm':
                self.pi.set_mode(pin_number, pigpio.OUTPUT)
                self.pi.set_PWM_frequency(pin_number, 0)
            else:
                raise ValueError(f"Invalid pin_type: {pin_type}")

            self.pin_map[gpio_name] = {
                'pin_number': pin_number,
                'pin_type': pin_type
            }

        return {"status": "OK", "initialized_pins": self.pin_map}

    def set_triggered_events(self, triggered_events):
        if not self.pin_map:
            raise ValueError("GPIO not initialized. Use initialize_gpio_pins.")

        for event in triggered_events:
            gpio_name = event['input_gpio_name']
            trigger_type = event.get('trigger_type', 'RISING_EDGE')
            delay_before_start = int(event.get('delay_before_start', 0))
            event_type = event['event_type']
            param1 = event['param1']
            param2 = event['param2']
            param3 = float(event.get('param3', 0))

            if gpio_name not in self.pin_map:
                raise ValueError(f"GPIO '{gpio_name}' is not initialized.")

            pin_number = self.pin_map[gpio_name]['pin_number']
            edge = pigpio.RISING_EDGE if trigger_type.lower() == 'rising_edge' else pigpio.FALLING_EDGE
            delay = delay_before_start / 1000

            def event_callback(gpio, level, tick):
                time.sleep(delay)
                if event_type.lower() == 'gpio':
                    gpio_name = param1
                    output_pin = self.pin_map.get(gpio_name, {}).get('pin_number')
                    if output_pin is not None:
                        if self.pin_map.get(gpio_name, {}).get("pin_type") == "PWM":
                            self.pi.set_PWM_frequency(output_pin, int(param2))
                        else:
                            self.pi.write(output_pin, 1 if param2.lower() == 'on' else 0)
                elif event_type.lower() == 'gpio_with_duration':
                    gpio_name = param1
                    output_pin = self.pin_map.get(gpio_name, {}).get('pin_number')
                    if output_pin is not None:
                        if self.pin_map.get(gpio_name, {}).get("pin_type") == "PWM":
                            self.pi.set_PWM_frequency(output_pin, int(param2))
                        else:
                            self.pi.write(output_pin, 1)
                        time.sleep(param3 / 1000)
                        if self.pin_map.get(gpio_name, {}).get("pin_type") == "PWM":
                            self.pi.set_PWM_frequency(output_pin, 0)
                        else:
                            self.pi.write(output_pin, 0)
                elif event_type.lower() == 'play_mp3':
                    self._play_mp3_files_in_background(param1)
                elif event_type.lower() == 'play_tones':
                    Hw_Abstraction.play_tones_in_background(param1)
                else:
                    raise ValueError(f"Invalid event type: {event_type}")

            callback = self.pi.callback(pin_number, edge, event_callback)
            self.event_callbacks[gpio_name] = callback

        return {"status": "OK", "configured_events": triggered_events}

    def set_timed_events(self, triggered_events):
        if not self.pin_map:
            raise ValueError("GPIO not initialized. Use initialize_gpio_pins.")

        for event in triggered_events:
            trigger_time = event['trigger_time']
            event_type = event['event_type']
            param1 = event.get('param1', None)
            param2 = event.get('param2', None)
            param3 = float(event.get('param3', 0))
            event_name = event['name']

            trigger_datetime = parser.parse(trigger_time)
            now = datetime.now(timezone.utc)
            delay = (trigger_datetime - now).total_seconds()

            if delay > 0:
                self._schedule_event(delay, event_type, param1, param2, param3, event_name)

        return {"status": "OK", "scheduled_events": triggered_events}

    def trigger_immediate_event(self, triggered_events):
        if not self.pin_map:
            raise ValueError("GPIO not initialized. Use initialize_gpio_pins.")

        for event in triggered_events:
            event_type = event['event_type']
            param1 = event.get('param1', None)
            param2 = event.get('param2', None)
            param3 = float(event.get('param3', 0))
            event_name = event['name']

            print(f"Triggering immediate event: {event_name}")

            if event_type.lower() == 'gpio':
                gpio_name = param1
                output_pin = self.pin_map.get(gpio_name, {}).get('pin_number')
                if output_pin is not None:
                    if self.pin_map.get(gpio_name, {}).get("pin_type") == "PWM":
                        self.pi.set_PWM_frequency(output_pin, int(param2))
                    else:
                        self.pi.write(output_pin, 1 if param2 == 'ON' else 0)
            elif event_type.lower() == 'gpio_with_duration':
                gpio_name = param1
                output_pin = self.pin_map.get(gpio_name, {}).get('pin_number')
                if output_pin is not None:
                    if self.pin_map.get(gpio_name, {}).get("pin_type") == "PWM":
                        self.pi.set_PWM_frequency(output_pin, int(param2))
                    else:
                        self.pi.write(output_pin, 1)
                    time.sleep(int(param2) / 1000)  # param2 is duration in milliseconds
                    if self.pin_map.get(gpio_name, {}).get("pin_type") == "PWM":
                        self.pi.set_PWM_frequency(output_pin, 0)
                    else:
                        self.pi.write(output_pin, 0)
            elif event_type.lower() == 'play_mp3':
                self.play_mp3_files_in_background(param1)
            elif event_type.lower() == 'play_tones':
                self.play_tones_in_background(param1)
            else:
                raise ValueError(f"Invalid event type: {event_type}")

        return {"status": "OK", "triggered_events": triggered_events}

    def delete_events(self, events):
        for event in events:
            event_name = event['name']

            if event_name in self.event_callbacks:
                self.event_callbacks[event_name].cancel()
                del self.event_callbacks[event_name]

            self.timed_events = [
                e for e in self.timed_events if e["name"] != event_name
            ]
        return {"status": "OK", "deleted_events": events}

    def delete_all_events(self):
        for callback in self.event_callbacks.values():
            callback.cancel()
        self.event_callbacks.clear()

        for event in self.timed_events:
            event['timer'].cancel()
        self.timed_events.clear()

        return {"status": "OK"}

    @staticmethod
    def play_tones_in_background(tones):
        def play_tones():
            audio_sequence = np.concatenate([Hw_Abstraction.generate_tone(tone["freq"], tone["duration"]) for tone in tones])
            play_obj = sa.play_buffer(audio_sequence, 1, 2, 44100)
            play_obj.wait_done()

        threading.Thread(target=play_tones, daemon=True).start()


    def _schedule_event(self, delay, event_type, param1, param2, param3, event_name):
        def event_task():
            print(f"Executing scheduled event: {event_name} at {datetime.now()}")
            if event_type.lower() == 'gpio':
                output_pin = self.pin_map.get(param1, {}).get('pin_number')
                if output_pin is not None:
                    if self.pin_map.get(param1, {}).get("pin_type") == "PWM":
                        self.pi.set_PWM_frequency(output_pin, int(param2))
                    else:
                        self.pi.write(output_pin, 1 if param2 == 'ON' else 0)
            elif event_type.lower() == 'gpio_with_duration':
                output_pin = self.pin_map.get(param1, {}).get('pin_number')
                if output_pin is not None:
                    if self.pin_map.get(param1, {}).get("pin_type") == "PWM":
                        self.pi.set_PWM_frequency(output_pin, int(param2))
                    else:
                        self.pi.write(output_pin, 1)
                    time.sleep(param3 / 1000)
                    if self.pin_map.get(param1, {}).get("pin_type") == "PWM":
                        self.pi.set_PWM_frequency(output_pin, 0)
                    else:
                        self.pi.write(output_pin, 0)
            elif event_type.lower() == 'play_mp3':
                Hw_Abstraction.play_mp3_files_in_background(param1)
            elif event_type.lower() == 'play_tones':
                Hw_Abstraction.play_tones_in_background(param1)
            else:
                raise ValueError(f"Invalid event type: {event_type}")

        timer = threading.Timer(delay, event_task)
        timer.start()

        self.timed_events.append({
            "name": event_name,
            "timer": timer,
            "trigger_time": (datetime.now() + timedelta(seconds=delay)).isoformat()
        })


    @staticmethod
    def generate_tone(frequency, duration, sample_rate=44100, amplitude=0.5):
        t = np.linspace(0, float(duration) / 1000, int(sample_rate * duration / 1000), False)
        wave = amplitude * np.sin(2 * np.pi * float(frequency) * t)
        audio = (wave * 32767).astype(np.int16)
        return audio

    @staticmethod
    def play_mp3_files_in_background(mp3_files):
        def play_files():
            for mp3_file in mp3_files:
                audio = AudioSegment.from_file(mp3_file)
                play(audio)
        threading.Thread(target=play_files, daemon=True).start()

    @staticmethod
    def testTone():
        Hw_Abstraction.play_tones_in_background([
            {"freq": 392, "duration": 500},
            {"freq": 440, "duration": 500},
            {"freq": 349, "duration": 500},
            {"freq": 174, "duration": 500},
            {"freq": 261, "duration": 1500},
        ])


if __name__ == '__main__':
    #Hw_Abstraction.play_mp3_files_in_background([f'./keep-the-change-ya-filthy-animal.mp3'])
    #time.sleep(5)
    Hw_Abstraction.testTone()
    time.sleep(5)
