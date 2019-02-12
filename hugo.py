import smbus
import time
import board
import digitalio
import busio
import adafruit_lis3dh

i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.D6)  
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)


address = 0x18

reg = 0x28

channel = 1

bus = smbus.SMBus(1)


while True:
    x_l = bus.read_byte_data(address,0x28|0x80)
    x_m = bus.read_byte_data(address,0x29|0x80)

    x = [x_l,x_m]

    int_x = int.from_bytes(x,'big')

    print(int_x/16380)

    time.sleep(1)


#xyz=bus.read_i2c_block_data(address,reg|0x80,6)

#print(xyz)

#x = xyz[0:2]

#x=int.from_bytes(x,'big')

#x=x/16380

#print(x)

