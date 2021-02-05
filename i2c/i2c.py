import smbus

from log import *


class I2cDevice:

    def __init__(self, bus, address):

        log(INFO, 'Setting up I2C device #{}:{}'.format(bus, address))

        self.bus     = smbus.SMBus(bus)
        self.address = address

        return

    def read_byte(self, register):

        return self.bus.read_byte_data(self.address, register)

    def write_byte(self, register, value):

        self.bus.write_byte_data(self.address, register, value)

        return
