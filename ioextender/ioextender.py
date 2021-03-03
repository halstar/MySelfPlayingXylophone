import i2c

from globals import *
from log     import *


class IoExtender:

    # MCP 23017 (a.k.a. our IO extender) registers

    MCP_23017_IODIRA = 0x00
    MCP_23017_IODIRB = 0x01
    MCP_23017_IPOLA  = 0x02
    MCP_23017_IPOLB  = 0x03
    MCP_23017_GPIOA  = 0x12
    MCP_23017_GPIOB  = 0x13
    MCP_23017_GPPUA  = 0x0C
    MCP_23017_GPPUB  = 0x0D
    MCP_23017_OLATA  = 0x14
    MCP_23017_OLATB  = 0x15

    IOS_COUNT = 16

    def __init__(self, bus, address):

        self.bus     = bus
        self.address = address

        self.i2c_device = i2c.I2cDevice(bus, address)

        log(INFO, 'Setup IO extender @{}:{}'.format(bus, address))

        # Configure all IOs as output, regular polarity
        self.i2c_device.write_byte(IoExtender.MCP_23017_IODIRA, 0x00)
        self.i2c_device.write_byte(IoExtender.MCP_23017_IODIRB, 0x00)
        self.i2c_device.write_byte(IoExtender.MCP_23017_IPOLA , 0x00)
        self.i2c_device.write_byte(IoExtender.MCP_23017_IPOLB , 0x00)

        # Clear all outputs
        self.i2c_device.write_byte(IoExtender.MCP_23017_GPIOA, 0x00)
        self.i2c_device.write_byte(IoExtender.MCP_23017_GPIOB, 0x00)
        self.i2c_device.write_byte(IoExtender.MCP_23017_OLATA, 0x00)
        self.i2c_device.write_byte(IoExtender.MCP_23017_OLATB, 0x00)

        # Store local status of all outputs, to avoid reading registers prior to their update
        self.port_a_values = 0x00
        self.port_b_values = 0x00

        return

    @staticmethod
    def __change_bit__(bitmap, bit, value):
        
        if value == 0:
            return bitmap & ~(1 << bit)
        else:
            return bitmap | (1 << bit)

    def write_io(self, pin, value):

        log(DEBUG, 'Writing IO on extender @{}/{}: {}/{}'.format(self.bus, self.address, pin, value))

        if not 0 <= pin <= IoExtender.IOS_COUNT - 1:

            log(ERROR, 'Cannot write IO; out of range pin: {}'.format(pin))
            return

        if pin < 8:

            new_values = self.__change_bit__(self.port_a_values, pin, value)
            self.i2c_device.write_byte(IoExtender.MCP_23017_OLATA, new_values)
            self.port_a_values = new_values

        else:

            new_values = self.__change_bit__(self.port_b_values, pin - 8, value)
            self.i2c_device.write_byte(IoExtender.MCP_23017_OLATB, new_values)
            self.port_b_values = new_values

        return

    def write_ios(self, pins_values):

        log(DEBUG, 'Writing IOs on extender @{}/{}: {}'.format(self.bus, self.address, pins_values))

        for pin_value in pins_values:

            if not 0 <= pin_value['pin'] <= IoExtender.IOS_COUNT - 1:

                log(ERROR, 'Cannot write IOS; out of range pin: {}'.format(pin_value['pin']))
                return

        port_a_values = self.port_a_values
        port_b_values = self.port_b_values

        for pin_value in pins_values:

            if pin_value['pin'] < 8:

                port_a_values = self.__change_bit__(port_a_values, pin_value['pin'], pin_value['value'])

            else:

                port_b_values = self.__change_bit__(port_b_values, pin_value['pin'] - 8, pin_value['value'])

        if port_a_values != self.port_a_values:

            self.i2c_device.write_byte(IoExtender.MCP_23017_OLATA, port_a_values)
            self.port_a_values = port_a_values

        if port_b_values != self.port_b_values:

            self.i2c_device.write_byte(IoExtender.MCP_23017_OLATB, port_b_values)
            self.port_b_values = port_b_values

        return

    def shutdown(self):

        log(INFO, 'Shutting down IO extender @{}/{}'.format(self.bus, self.address))

        # Turn off all output
        self.i2c_device.write_byte(IoExtender.MCP_23017_OLATA, 0x00)
        self.i2c_device.write_byte(IoExtender.MCP_23017_OLATB, 0x00)

        return
