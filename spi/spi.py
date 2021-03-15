import spidev

from log import *


class SpiDevice:

    def __init__(self, bus, address, max_speed):

        log(INFO, 'Setting up SPI device #{}:{}@{}Hz'.format(bus, address, max_speed))

        self.bus                 = bus
        self.address             = address
        self.device              = spidev.SpiDev(bus, address)
        self.device.mode         = 0
        self.device.max_speed_hz = max_speed

        return

    def write_bytes(self, data):

        return self.device.writebytes(data)

    def close(self):

        log(INFO, 'Closing SPI device #{}:{}'.format(self.bus, self.address))

        self.device.close()

        return
