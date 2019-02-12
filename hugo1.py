import smbus
import time
import board
import busio
import json
import _thread
import paho.mqtt.client as mqtt

def on_message(client, userdata, message) :
    print("Received message:{} on topic {}".format(message.payload, message.topic))

DIVIDER = 16380

client = mqtt.Client()
#client.tls_set(ca_certs="mosquitto.org.crt",certfile="client.crt",keyfile="client.key")
print(client.connect("test.mosquitto.org",port=1883))
# msg = input()
# msg_info = client.publish("IC.embedded/HAGI/test",msg)
#msg_info is result of publish()

client.subscribe("IC.embedded/HAGI/#")
client.on_message = on_message
client.loop_start()

# Create library object using our Bus I2C port
#i2c = busio.I2C(board.SCL, board.SDA)
bus = smbus.SMBus(1)

bus.write_byte_data(0x18, 0x20, 0x27)
bus.write_byte_data(0x18, 0x23, 0x00)

time.sleep(0.5)

# Initialize communication with the sensor, using the default 16 samples per conversion.
# This is the best accuracy but a little slower at reacting to changes.
# The first sample will be meaningless


def temperature():
    while True:
        obj = bus.read_i2c_block_data(0x40,0x03,2)
        raw = bus.read_i2c_block_data(0x40,0x01,2)
        #print(obj)
        #print(raw)
        int_obj=int.from_bytes(obj,'big')
        int_raw=int.from_bytes(raw,'big')
        obj_temp=int_obj*0.03125/4
        die_temp=int_raw*0.03125/4
        #print(temp)
        #print(die)

        data = {
            "temperature":{
                "die": die_temp,
                "object": obj_temp
            }
        }


        json_string = json.dumps(data)

        client.publish("IC.embedded/HAGI",json_string)
        print("tmp")
        time.sleep(5)


def acc():
    while True:
        x_lsb = bus.read_byte_data(0x18, 0x28)
        x_msb = bus.read_byte_data(0x18, 0x29)

        x = x_msb * 256 + x_lsb
        if x > 32767 :
        	x -= 65536


        #y
        y_lsb = bus.read_byte_data(0x18, 0x2A)
        y_msb = bus.read_byte_data(0x18, 0x2B)

        y = y_msb * 256 + y_lsb
        if y > 32767 :
        	y -= 65536


        #z
        z_lsb = bus.read_byte_data(0x18, 0x2C)
        z_msb = bus.read_byte_data(0x18, 0x2D)

        z = z_msb * 256 + z_lsb
        if z > 32767 :
        	z -= 65536

        x = x/DIVIDER
        y = y/DIVIDER
        z = z/DIVIDER

        data1 = {
            "axis":{
                "x": x,
                "y": y,
                "z": z
            }
        }


        json_string1 = json.dumps(data1)

        client.publish("IC.embedded/HAGI",json_string1)
        print("acc")
        time.sleep(1)


try:
   _thread.start_new_thread( temperature,() )
   _thread.start_new_thread( acc,() )
except:
   print("Error: unable to start thread")

while 1:
   pass