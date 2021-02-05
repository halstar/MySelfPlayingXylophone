import spidev

from log import *


class SpiDevice:

    def __init__(self, bus, address):

        log(INFO, 'Setting up I2C device #{}:{}'.format(bus, address))

        self.device              = spidev.SpiDev()
        self.device.speed        = 500000
        self.device.mode         = 1
        self.device.max_speed_hz = self.speed

        self.device.open(bus, address)

        return

    def read_byte(self, register):

        return self.device.xfer2(register)

    def write_byte(self, register, value):

        return self.device.xfer2([register, value])
