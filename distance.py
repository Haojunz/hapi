import time
import smbus

bus = smbus.SMBus(1)

x = bus.read_i2c_block_data(0x29,0x14,2)

int_x = int.from_bytes(x,'big')

print(int_x)
