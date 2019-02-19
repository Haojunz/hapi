import smbus
import time
import json
from random import seed
from random import gauss
import _thread
import paho.mqtt.client as mqtt
import adafruit_lis3dh
import board
import digitalio
import busio
import adafruit_vl53l0x
from decimal import Decimal


seed(1)
DIVIDER = 16380
TEMP_UPPER_LIMIT = 37 #C
DIS_LOWER_LIMIT = 40 #mm
DIE_TEMP_UPPER_LIMIT = 37 #C


# Hardware I2C setup. Use the CircuitPlayground built-in accelerometer if available;
# otherwise check I2C pins.
if hasattr(board, 'ACCELEROMETER_SCL'):
    i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
    int1 = digitalio.DigitalInOut(board.ACCELEROMETER_INTERRUPT)
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19, int1=int1)
else:
    i2c = busio.I2C(board.SCL, board.SDA)
    int1 = digitalio.DigitalInOut(board.D6)  # Set to correct pin for interrupt!
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)

# Set range of accelerometer (can be RANGE_2_G, RANGE_4_G, RANGE_8_G or RANGE_16_G).
lis3dh.range = adafruit_lis3dh.RANGE_2_G


def on_message(client, userdata, message) :
    print("Received message:{} on topic {}".format(message.payload, message.topic))

client = mqtt.Client()
#client.tls_set(ca_certs="mosquitto.org.crt",certfile="client.crt",keyfile="client.key")

# print(client.connect("test.mosquitto.org",port=1883))
print(client.connect("ee-estott-octo.ee.ic.ac.uk",port=1883))

#client.subscribe("IC.embedded/HAGI/#")
#client.on_message = on_message
#client.loop_start()

i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

bus = smbus.SMBus(1)

bus.write_byte_data(0x18, 0x20, 0x27)
bus.write_byte_data(0x18, 0x23, 0x00)

time.sleep(0.5)


def measure_temp (temp_delay):
    global die_temp
    global obj_temp
    global alert
    # global x
    # global y
    # global z
    global s
    global d
    #die_temp = 0
    #obj_temp = 0
    alert = 0
    die_alert = 0
    # x = 0
    # y = 0
    # z = 0
    s = 0
    d = 0
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

        alert = 0
        die_alert = 0

        if obj_temp>=TEMP_UPPER_LIMIT:
            noise = abs(gauss(0,1))
            obj_temp = round(TEMP_UPPER_LIMIT+noise,2)
            alert = 1

        if die_tempe>=DIE_TEMP_UPPER_LIMIT:
            die_alert = 1


        obj_temp = round(obj_temp,2)
        die_temp = round(die_temp,2)


        print(obj_temp)

        print(die_temp)

        # temp = {
        #     "temperature":{
        #         "die": die_temp,
        #         "object": obj_temp,
        #         "alert": alert
        #     },
        #     "axis":{
        #         "x": x,
        #         "y": y,
        #         "z": z
        #     },
        #     "distance": d
        # }

        temp = {
            "temperature":{
                "die": die_temp,
                "object": obj_temp,
                "alert": alert,
                "die_alert": die_alert
            },
            "shake": s,
            "distance": d
        }


        json_temp = json.dumps(temp)

        print(json_temp)

        #print("tmp")
        client.publish("IC.embedded/HAGI/test",json_temp)

        time.sleep(temp_delay)


def measure_acc(acc_delay,threshold):
    global die_temp
    global obj_temp
    global alert
    # global x
    # global y
    # global z
    global s
    global d
    #die_temp = 0
    #obj_temp = 0
    alert = 0
    die_alert = 0
    # x = 0
    # y = 0
    # z = 0
    s = 0
    d = 0
    while True:

        # s = 0

        if lis3dh.shake(shake_threshold=threshold):
            s = s + 1
            print("Shaken!")
        # x_lsb = bus.read_byte_data(0x18, 0x28)
        # x_msb = bus.read_byte_data(0x18, 0x29)
        #
        # x = x_msb * 256 + x_lsb
        # if x > 32767 :
        # 	x -= 65536
        #
        #
        # #y
        # y_lsb = bus.read_byte_data(0x18, 0x2A)
        # y_msb = bus.read_byte_data(0x18, 0x2B)
        #
        # y = y_msb * 256 + y_lsb
        # if y > 32767 :
        # 	y -= 65536
        #
        #
        # #z
        # z_lsb = bus.read_byte_data(0x18, 0x2C)
        # z_msb = bus.read_byte_data(0x18, 0x2D)
        #
        # z = z_msb * 256 + z_lsb
        # if z > 32767 :
        # 	z -= 65536
        #
        # x = x/DIVIDER
        # y = y/DIVIDER
        # z = z/DIVIDER
        #
        # print(x)
        #
        # print(y)
        #
        # print(z)

        # xyz = {
        #     "temperature":{
        #         "die": die_temp,
        #         "object": obj_temp,
        #         "alert": alert
        #     },
        #     "axis":{
        #         "x": x,
        #         "y": y,
        #         "z": z
        #     },
        #     "distance": d
        # }

        xyz = {
            "temperature":{
                "die": die_temp,
                "object": obj_temp,
                "alert": alert,
                "die_alert": die_alert
            },
            "shake": s,
            "distance": d
        }


        json_xyz = json.dumps(xyz)

        print(json_xyz)

        #print("acc")
        client.publish("IC.embedded/HAGI/test",json_xyz)

        time.sleep(acc_delay)


def measure_distance(distance_delay):
    global die_temp
    global obj_temp
    global alert
    # global x
    # global y
    # global z
    global s
    global d
    #die_temp = 0
    #obj_temp = 0
    alert = 0
    die_alert = 0
    # x = 0
    # y = 0
    # z = 0
    s = 0
    d = 0
    while True:

        d = vl53.range

        #print(x)

        if d < DIS_LOWER_LIMIT:
            d = 0 # x = o if too close -> alert
            alert = 1

        # distance = {
        #     "temperature":{
        #         "die": die_temp,
        #         "object": obj_temp,
        #         "alert": alert
        #     },
        #     "axis":{
        #         "x": x,
        #         "y": y,
        #         "z": z
        #     },
        #     "distance": d
        # }

        d = d/10 # mm -> cm
      

        distance = {
            "temperature":{
                "die": die_temp,
                "object": obj_temp,
                "alert": alert,
                "die_alert": die_alert
            },
            "shake": s,
            "distance": d
        }

        json_distance = json.dumps(distance)

        print(json_distance)

        client.publish("IC.embedded/HAGI",json_distance)

        time.sleep(distance_delay)


try:
   _thread.start_new_thread( measure_temp, (5,) )
   _thread.start_new_thread( measure_acc, (0.1, 10,) )
   _thread.start_new_thread( measure_distance, (0.2,) )
except:
   print("Error: unable to start thread")

while 1:
   pass
