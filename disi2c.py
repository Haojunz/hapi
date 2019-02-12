VL53L0X_REG_IDENTIFICATION_MODEL_ID=0xc0
VL53L0X_REG_IDENTIFICATION_REVISION_ID=0xc2
VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD=  0x50
VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD=0x70
VL53L0X_REG_SYSRANGE_START=0x00
VL53L0X_REG_RESULT_INTERRUPT_STATUS=0x13
VL53L0X_REG_RESULT_RANGE_STATUS=0x14
sensor= 0x29#I2C Address


print("Revision ID ")
print(i2c.readfrom_mem(sensor,VL53L0X_REG_IDENTIFICATION_REVISION_ID,1))
print("")
print("Device ID ")
print(i2c.readfrom_mem(sensor,VL53L0X_REG_IDENTIFICATION_MODEL_ID,1))
print("")
print("Pre Range config Period")
print(i2c.readfrom_mem(sensor,VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD,1))
print("")
print("Final  Period")
print(i2c.readfrom_mem(sensor,VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD,1))

#To read first check the status
val=i2c.readfrom_mem(sensor,VL53L0X_REG_RESULT_RANGE_STATUS,1)

#if val is equal to 64 then it read the distance 

#read the value
datasensor=i2c.readfrom_mem(sensor,0x14,12)#Read sensor data
distance=datasensor[10]*256+datasensor[11]#combine integers
