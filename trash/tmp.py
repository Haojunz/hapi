import time
import board
import busio
import adafruit_tmp007
 
# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0
 
 
 
# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tmp007.TMP007(i2c)
 
 
tmp = {} 
i = 1

# Initialize communication with the sensor, using the default 16 samples per conversion.
# This is the best accuracy but a little slower at reacting to changes.
# The first sample will be meaningless
while i<13:
    die_temp = sensor.die_temperature
   # print('   Die temperature: {0:0.3F}*C / {1:0.3F}*F'.format(die_temp, c_to_f(die_temp)))
    obj_temp = sensor.temperature
   # print('Object temperature: {0:0.3F}*C / {1:0.3F}*F'.format(obj_temp, c_to_f(obj_temp)))
    tmp.update({'die_temp':die_temp,'obj_temp':obj_temp})
    print(tmp)
    i+=1
    time.sleep(5.0)
