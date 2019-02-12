import smbus
import time

DIVIDER = 16380

bus = smbus.SMBus(1)

bus.write_byte_data(0x18, 0x20, 0x27)
bus.write_byte_data(0x18, 0x23, 0x00)

time.sleep(0.5)

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


    time.sleep(1)
