import smbus
import time


bus = smbus.SMBus(1)

bus.write_byte_data(0x29, 0xC0, 0xEE)
bus.write_byte_data(0x29, 0xC1, 0xAA)
bus.write_byte_data(0x29, 0xC2, 0x10)
bus.write_byte_data(0x29, 0x51, 0x0099)
bus.write_byte_data(0x29, 0x61, 0x0000)

time.sleep(0.5)

while True:

    datasensor=bus.read_i2c_block_data(0x18,0x14,12)#Read sensor data
    distance=datasensor[10]*256+datasensor[11]

    print(distance)

    time.sleep(1)
