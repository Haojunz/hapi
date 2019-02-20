######## Import libraries needed ########
# p.s. libraries of sensors are not included
import smbus
import time
import json
import _thread
from decimal import Decimal
import math
import paho.mqtt.client as mqtt

######## Pre-defined parameters ########
DIVIDER = 16380 # Pre-defined parameter used for calculation of acceleration
TEMP_UPPER_LIMIT = 35 # Unit: C°
DIS_LOWER_LIMIT = 4 # Unit: cm
DIE_TEMP_UPPER_LIMIT = 30 #Unit: C°
SHAKE_THRES = 11 # Shake threshold
DISTANCE_DELAY = 0.2 # Delay of distance sensor = 1/Rate of distance sensor
ACC_DELAY = 0.1 # Delay of accelerometer = 1/Rate of accelerometer
TEMP_DELAY = 5 # Delay of therometer = 1/Rate of therometer


######## Pre-defined functions & settings ########
def on_message(client, userdata, message) :
    print("Received message:{} on topic {}".format(message.payload, message.topic))

client = mqtt.Client()
#client.tls_set(ca_certs="mosquitto.org.crt",certfile="client.crt",keyfile="client.key")
#print(client.connect("test.mosquitto.org",port=1883))
print(client.connect("ee-estott-octo.ee.ic.ac.uk",port=1883))

## Received part:
#client.subscribe("IC.embedded/HAGI/#")
#client.on_message = on_message
#client.loop_start()


bus = smbus.SMBus(1) # Create the i2c bus
                     # Bus address of therometer:0x40
                     # Bus address of accelerometer:0x18
                     # Bus address of distance sensor:0x29


bus.write_byte_data(0x18, 0x20, 0x27) # setup for the accelerometer with i2c addr 0x18: write command 0x27 into register with addr 0x20
bus.write_byte_data(0x18, 0x23, 0x00) # write command 0x00 into register with addr 0x23

time.sleep(0.5)

# function used to measure object temperature(obj_temp) & environment temperature(die_temp)
def measure_temp (delay):

    while True:
        obj = bus.read_i2c_block_data(0x40,0x03,2)      # read 2-bytes data which contains object temperature from therometer with i2c addr 0x40 through register with addr 0x03
        raw = bus.read_i2c_block_data(0x40,0x01,2)      # read the data contain die temperature from output register with addr 0x01

        int_obj = int.from_bytes(obj,'big')       # convert bytes into integer
        int_raw = int.from_bytes(raw,'big')

        obj_temp = int_obj*0.03125/4      # algorithm from data sheet to calculate object temperature
        die_temp = int_raw*0.03125/4      # algorithm from data sheet to calculate die temperature

        alert = 0       # initially there is no (die_)alarm so (die_)alarm = 0
        die_alert = 0

        if obj_temp >= TEMP_UPPER_LIMIT:      # if object temperature is higer than the upper limit
            alert = 1       # alarm is 1(actived)

        if die_temp >= DIE_TEMP_UPPER_LIMIT:      # if die temperature is higer than the upper limit
            die_alert = 1       # die_alarm = 1(actived)

        obj_temp = round(obj_temp,2)        # truncate the obj_temp into two-decimals precision
        die_temp = round(die_temp,2)        # truncate the die_temp into two-decimals precision

        temp = {                            # data structure that stores the information
            "temperature":{
                "die": die_temp,
                "object": obj_temp,
                "alert": alert,
                "die_alert": die_alert
            }
        }

        json_temp = json.dumps(temp)        # convert the data structure into json byte-encoded string for transmitting
        print(json_temp)                    # for debugging
        client.publish("IC.embedded/HAGI",json_temp)       # transmit via mqtt with topic IC.embedded/HAGI

        time.sleep(delay)       # not measure too frequently for higher accuracy
                                # (5s is needed for therometer to get accurate reading according to datasheet)

# sub-function used in measure_shake to measure the acceleration in 3 axis
def acc():

    # x-axis
    x_lsb = bus.read_byte_data(0x18, 0x28)      # read the least significant byte of x from output register with addr 0x28
    x_msb = bus.read_byte_data(0x18, 0x29)      # read the most significant byte of x  from output register with addr 0x29

    x = x_msb * 256 + x_lsb     # same as int.from_bytes which convert bytes into integer
    if x > 32767 :      # algorithm for measurign x
    	x -= 65536

    # y-axis
    y_lsb = bus.read_byte_data(0x18, 0x2A)      # read the least significant byte of y from output register with addr 0x2A
    y_msb = bus.read_byte_data(0x18, 0x2B)      # read the most significant byte of y from output register with addr 0x2B

    y = y_msb * 256 + y_lsb     # same as int.from_bytes which convert bytes into integer
    if y > 32767 :      # algorithm for measuring y
    	y -= 65536

    # z-axis
    z_lsb = bus.read_byte_data(0x18, 0x2C)      # read the least significant byte of z from output register with addr 0x2C
    z_msb = bus.read_byte_data(0x18, 0x2D)      # read the most significant byte of z from output register with addr 0x2D

    z = z_msb * 256 + z_lsb     # same as int.from_bytes which convert bytes into integer
    if z > 32767 :       # algorithm for measuring y
    	z -= 65536

    x = x/DIVIDER       # algorithm from data sheet for 3 axis sensing
    y = y/DIVIDER
    z = z/DIVIDER

    return (x,y,z)

# function used to sense the movement of accelerometer, i.e. whether the accelerometer is shaked sufficiently (set by SHAKE_THRES)
def measure_shake(delay,shake_threshold):

    avg_count = 10      # how many measurements need before calculating the average result
    total_delay = 0.1       # total time need for all measurements

    while True:
        shake_accel = (0, 0, 0)     # Initialize parameters
        shake = 0       # define shake = 0 if there is not a shake

        for _ in range(avg_count):      # for avg_count times of measurements
            shake_accel = tuple(map(sum, zip(shake_accel, acc())))      # add up values from each measurement
            time.sleep(total_delay / avg_count)     # sleep between each measurement for higher accuracy

        avg = tuple(value / avg_count for value in shake_accel)     # calculate the average value of 10 times measurements
        total_accel = 10*math.sqrt(sum(map(lambda x: x * x, avg)))      # algorithm from data sheet to calculate the total amount shake

        if total_accel > shake_threshold:       # if total amount of shake is larger than the threshould
            shake = 1                           # then there is a shake

        acc_data = {
            "shake": shake                      # data structure for the transmitted data
        }

        json_acc = json.dumps(acc_data)     # convert into json string for mqtt transmission
        print(json_acc)     # for debugging
        client.publish("IC.embedded/HAGI",json_acc)        # sending data by mqtt with topic IC.embedded/HAGI

        time.sleep(delay)       # sleep between each measurement


# sub-function used in measure_distance to convert two bytes into an integer
def make_16bit_int(lsb, msb): # lsb: least significant byte; msb: most significant byte
    return (msb << 8) | lsb

# function used to measure distance
def measure_distance(delay):
    distance = 819.0 # pre-set the distance to 819.0 cm, which is an indicator of out-of-range readings,
                     # at the start before the sensor is ready to give normal readings;
                     # otherwise a few 0s will be generated before the sensor gives normal readings.
    while True:

        bus.write_byte_data(0x29, 0x000, 0x01) # Writing 0x01 in the starting address 0x000 to active the reading
        distance_data = bus.read_i2c_block_data(0x29, 0x14, 12) # store the reading data

        distance = make_16bit_int(distance_data[11], distance_data[10]) # Eleventh and twelfth byte contain the distance data.

        distance = distance/10 # Covert unit from mm to cm

        if distance < DIS_LOWER_LIMIT:
            distance = 0 # distance = o if too close -> alert actived in app

        # Package the data in terms of json form structure
        distance_data = {
            "distance": distance
        }

        # Convert it to json byte-encoded string and publish it in the topic.
        json_distance = json.dumps(distance_data) # convert into json string for mqtt transmission
        print(json_distance) # for debugging
        client.publish("IC.embedded/HAGI",json_distance) # transmit via mqtt with topic IC.embedded/HAGI

        time.sleep(delay)


######## Main function ########
# Threading is used because our sensors are set at different rates.
try:
   _thread.start_new_thread( measure_temp, (TEMP_DELAY,) )
   _thread.start_new_thread( measure_shake, (ACC_DELAY, SHAKE_THRES,) )
   _thread.start_new_thread( measure_distance, (DISTANCE_DELAY,) )
except:
   print("Error: unable to start thread")


while 1:
   pass

