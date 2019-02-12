import _thread
import time
import smbus
import board
import busio
import json
import paho.mqtt.client as mqtt

DIVIDER = 16380

def on_message(client, userdata, message) :
   print("Received message:{} on topic {}".format(message.payload, message.topic))



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


def read_temp():
    while True:

        #bus.write_byte(0x40,0x03)
        obj = bus.read_i2c_block_data(0x40,0x03,2)
        raw = bus.read_i2c_block_data(0x40,0x01,2)
        #print(obj)
        #print(raw)
        int_obj=int.from_bytes(obj,'big')
        int_raw=int.from_bytes(raw,'big')
        obj_temp=int_obj*0.03125/4
        die_temp=int_raw*0.03125/4

        print(obj_temp)
        print(die_temp)
        print("obj_temp = %f , die_temp = %f ," % (obj_temp,die_temp))

        temp = {
            "temperature":{
                "die": die_temp,
                "object": obj_temp
            }
        }


        json_string_temp = json.dumps(temp)

        client.publish("IC.embedded/HAGI/test",json_string_temp)

        time.sleep(5.0)


def read_acc():
    while True:

        #x
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

        # Output data to screen
        # print(x,y,z)
        print("x = %0.3f G, y = %0.3f G, z = %0.3f G" % (x, y, z))

        acc = {
            "acceleration":{
                "x-axis": x,
                "y-axis": y,
                "z-axis": z,
            }
        }


        json_string_acc = json.dumps(acc)

        client.publish("IC.embedded/HAGI/test",json_string_acc)

        time.sleep(1)



try:
   _thread.start_new_thread( read_temp,() )
   _thread.start_new_thread( read_acc,() )
except:
   print ("Error: unable to start thread")

while 1:
   pass
