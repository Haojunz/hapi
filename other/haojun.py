#!/usr/bin/python
# Author: Adapted to CircuitPython by Jerry Needell
#     Adafruit_Python_TMP example by Tony DiCola
#

import time
import board
import busio
import adafruit_tmp007
import json
import paho.mqtt.client as mqtt

# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

def on_message(client, userdata, message) :
    print("Received message:{} on topic {}".format(message.payload, message.topic))



client = mqtt.Client()
client.tls_set(ca_certs="mosquitto.org.crt",certfile="client.crt",keyfile="client.key")
print(client.connect("test.mosquitto.org",port=8884))
# msg = input()
# msg_info = client.publish("IC.embedded/HAGI/test",msg)
#msg_info is result of publish()

client.subscribe("IC.embedded/HAGI/#")
client.on_message = on_message
client.loop_start()

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tmp007.TMP007(i2c)

# Initialize communication with the sensor, using the default 16 samples per conversion.
# This is the best accuracy but a little slower at reacting to changes.
# The first sample will be meaningless
while True:
    die_temp = sensor.die_temperature
    #print('   Die temperature: {0:0.3F}*C / {1:0.3F}*F'.format(die_temp, c_to_f(die_temp)))
    obj_temp = sensor.temperature
    #print('Object temperature: {0:0.3F}*C / {1:0.3F}*F'.format(obj_temp, c_to_f(obj_temp)))

    data = {
        "temperature":{
            "die": die_temp,
            "object": obj_temp
        }
    }

    # dietemp = str(die_temp)

    json_string = json.dumps(data)

    #print(data)
    #print(json_string)
    # with open("data_file.json", "w") as write_file:
    #     json.dump(data, write_file)
    # client.publish("IC.embedded/HAGI/test",dietemp)
    client.publish("IC.embedded/HAGI/test",json_string)

    time.sleep(5.0)
