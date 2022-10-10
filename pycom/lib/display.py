# display.py - Functions for interacting with the touchscreen display
import config
import time
from machine import Pin, SPI
import ustruct 
from micropython import const

# Constants for display
REG_HCYCLE = const(0x30202C)
REG_HSIZE = const(0x302034)
REG_HOFFSET = const(0x302030)
REG_HSYNC0 = const(0x302038)
REG_HSYNC1 = const(0x30203C)
REG_VCYCLE = const(0x302040)
REG_VOFFSET = const(0x302044)
REG_VSIZE = const(0x302048)
REG_VSYNC0 = const(0x30204C)
REG_VSYNC1 = const(0x302050)
REG_SWIZZLE = const(0x302064)
REG_PCLK_POL = const(0x30206C)
REG_CSPREAD = const(0x302068)
RAM_DL = const(0x300000)
RAM_DL_4 = const(0x300004)
RAM_DL_8 = const(0x300008)
REG_DLSWAP = const(0x302054)
REG_GPIO_DIR = const(0x302090)
REG_GPIO = const(0x302094)
REG_PCLK = const(0x302070)
CLKINT = const(0x48)
ACTIVE = const(0X00)
REG_ID = const(0x302000)

# Present recommendations to user
def display_recommendations(msg):
    print("Running display_recommendations()")
    user_id = msg[0]
    # Check if there are recommendations available
    if len(msg) > 1:
        recs = msg[1:]
        print("Displaying recommendations for user ", user_id)
        # DISPLAY ON TOUCHSCREEN
        for i in recs:
            print(config.locations[int(i)])
    else:
        # DISPLAY ERROR ON TOUCHSCREEN
        print("No recommendations available")
    return

# Get inputs from touchscreen
def get_inputs(id):
    print("Running get_inputs()")
    # GET USER FEEDBACK FROM SCREEN
    rating = '5'
    context = 'sports'

    user = str(id)
    location = str(config.DEVICE_ID)
    json_data = {
        'user' : user,
        'rating' : rating,
        'location' : location,
        'context' : context
    }
    return json_data

# Display code adapted from vitormhenrique's code
# Available here: https://forum.micropython.org/viewtopic.php?t=5884
# Display class
class FT1X_HAL:
    def __init__(self, spi, cs):
        self._spi = spi
        self._cs = cs
        cs.init(cs.OUT, value=1)

    def write_cmd(self, command):
        self._cs.value(0)
        self._spi.write(bytearray([command, 0x00, 0x00]))
        self._cs.value(1)

    def read8(self, address):
        self._cs.value(0)
        self._spi.write(bytearray([address >> 16, address >> 8, address, 0x00]))
        data = self._spi.read(1)
        self._cs.value(1)
        return ustruct.unpack(">B", data)[0]

class FT1X(FT1X_HAL):
    def begin(self):
        self.write_cmd(ACTIVE)
        self.write_cmd(CLKINT)

        time.sleep(0.3)

        chipid = self.read8(REG_ID) 

        count = 0
        # Attempt to read display device ID register
        while chipid != 0x7C:
            chipid = self.read8(REG_ID)
            print(chipid)
            time.sleep(0.1)
            count += 1
            if count > 100000000:
                print("timed out")
                break

        print("id read: {}".format(chipid))
        # Send startup commands after ID is read
        self._spi.write(bytearray([REG_HCYCLE >> 16, REG_HCYCLE >> 8, REG_HCYCLE, 0x02, 0x24]))
        self._spi.write(bytearray([REG_HOFFSET >> 16, REG_HOFFSET >> 8, REG_HOFFSET, 0x2B]))
        self._spi.write(bytearray([REG_HSYNC0 >> 16, REG_HSYNC0 >> 8, REG_HSYNC0, 0x00]))
        self._spi.write(bytearray([REG_HSYNC1 >> 16, REG_HSYNC1 >> 8, REG_HSYNC1, 0x29]))

        self._spi.write(bytearray([REG_VCYCLE >> 16, REG_VCYCLE >> 8, REG_VCYCLE, 0x01, 0x24]))
        self._spi.write(bytearray([REG_VOFFSET >> 16, REG_VOFFSET >> 8, REG_VOFFSET, 0x0C]))
        self._spi.write(bytearray([REG_VSYNC0 >> 16, REG_VSYNC0 >> 8, REG_VSYNC0, 0x00]))
        self._spi.write(bytearray([REG_VSYNC1 >> 16, REG_VSYNC1 >> 8, REG_VSYNC1, 0x0A]))

        self._spi.write(bytearray([REG_SWIZZLE >> 16, REG_SWIZZLE >> 8, REG_SWIZZLE, 0x00]))
        self._spi.write(bytearray([REG_PCLK_POL >> 16, REG_PCLK_POL >> 8, REG_PCLK_POL, 0x01]))
        self._spi.write(bytearray([REG_CSPREAD >> 16, REG_CSPREAD >> 8, REG_CSPREAD, 0x01]))
        self._spi.write(bytearray([REG_HSIZE >> 16, REG_HSIZE >> 8, REG_HSIZE, 0x01, 0xE0]))
        self._spi.write(bytearray([REG_VSIZE >> 16, REG_VSIZE >> 8, REG_VSIZE, 0x01, 0x10]))

        self._spi.write(bytearray([RAM_DL >> 16, RAM_DL >> 8, RAM_DL, 0x02, 0x00, 0x00, 0x00]))
        self._spi.write(bytearray([RAM_DL_4 >> 16, RAM_DL_4 >> 8, RAM_DL_4, 0x26, 0x00, 0x00, 0x04]))
        self._spi.write(bytearray([RAM_DL_8 >> 16, RAM_DL_8 >> 8, RAM_DL_8, 0x00, 0x00, 0x00, 0x00]))
        self._spi.write(bytearray([REG_DLSWAP >> 16, REG_DLSWAP >> 8, REG_DLSWAP, 0x02]))
        self._spi.write(bytearray([REG_GPIO_DIR >> 16, REG_GPIO_DIR >> 8, REG_GPIO_DIR, 0x80]))
        self._spi.write(bytearray([REG_GPIO >> 16, REG_GPIO >> 8, REG_GPIO, 0x080]))
        self._spi.write(bytearray([REG_PCLK >> 16, REG_PCLK >> 8, REG_PCLK, 0x05]))

## Used for display testing
# spi = SPI(0, baudrate=8000000, polarity=0, phase=0)
# gpu = FT1X(spi, cs=Pin('P4', mode = Pin.OUT))
# gpu.begin()