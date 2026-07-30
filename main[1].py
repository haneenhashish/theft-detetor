import network
import time
from machine import Pin, PWM
from umqtt.simple import MQTTClient

SSID = "Wokwi-GUEST"
PASSWORD = ""

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_MOTION = b"team/motion"
TOPIC_ARM = b"team/arm"
CLIENT_ID = "esp32-alarm-" + str(time.ticks_ms())

pir = Pin(27, Pin.IN)
led = Pin(25, Pin.OUT)
buzzer = PWM(Pin(26))
buzzer.duty(0)

armed = True

def connect_wifi(ssid = 'Wokwi-GUEST', pwd = ''):
    Wifi_connection = network.WLAN(network.STA_IF)
    Wifi_connection.active(True)
    Wifi_connection.connect(ssid, pwd)

    while not Wifi_connection.isconnected():
        pass

    print('Wifi is OK')
    return Wifi_connection


def on_message(topic, msg):
    global armed
    if topic == TOPIC_ARM:
        armed = (msg == b"ON")

def sound_buzzer(on):
    if on:
        buzzer.freq(1000)
        buzzer.duty(512)
    else:
        buzzer.duty(0)

def main():
    global armed
    connect_wifi()

    client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(TOPIC_ARM)

    while True:
        client.check_msg()
        motion_detected = pir.value()

        if armed and motion_detected == 1:
            led.value(1)
            sound_buzzer(True)
            client.publish(TOPIC_MOTION, b"INTRUDER DETECTED")
            print("Motion detected")
            time.sleep(0.5)
        else:
            led.value(0)
            sound_buzzer(False)
            print("No motion")

        time.sleep(0.2)

main()