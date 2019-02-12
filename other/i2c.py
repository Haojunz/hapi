import smbus
bus = smbus.SMBus(1)
#bus.write_byte(0x40,0x03)
obj = bus.read_i2c_block_data(0x40,0x03,2)
raw = bus.read_i2c_block_data(0x40,0x01,4)
print(obj)
print(raw)
int_obj=int.from_bytes(obj,'big')
if int_obj & 1:
	int_obj=-9999
int_raw=int.from_bytes(raw,'big')
temp=int_obj*0.03125/4
die=int_raw*0.03125/4
print(temp)
print(die)
