import time
import RPi.GPIO
import spi

from log     import *
from globals import *


class EInkScreen:

    PARTIAL_DISPLAY_LUT = [
        0x0,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x80,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x40,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0A,0x0,0x0,0x0,0x0,0x0,0x2,
        0x1,0x0,0x0,0x0,0x0,0x0,0x0,
        0x1,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,
        0x22,0x17,0x41,0xB0,0x32,0x36
    ]

    def __init__(self, bus, address):

        log(INFO, 'Setting up E-ink screen class')

        self.spi_device = spi.SpiDevice(bus, address)

        return

    def __send_command__(self, command):

        log(DEBUG, "Sending command: 0x{:02X}".format(command))

        RPi.GPIO.output(E_INK_SCREEN_DC_PIN, 0)
        RPi.GPIO.output(E_INK_SCREEN_CS_PIN, 0)
        self.spi_device.write_bytes([command])
        RPi.GPIO.output(E_INK_SCREEN_CS_PIN, 1)

        return

    def __send_data__(self, data):

        # No log while sending data or console would be flooded

        RPi.GPIO.output(E_INK_SCREEN_DC_PIN, 1)
        RPi.GPIO.output(E_INK_SCREEN_CS_PIN, 0)
        self.spi_device.write_bytes([data])
        RPi.GPIO.output(E_INK_SCREEN_CS_PIN, 1)

        return

    @staticmethod
    def __read_busy__():

        log(DEBUG, "E-ink screen busy")

        # 0: idle, 1: ready
        while RPi.GPIO.input(E_INK_SCREEN_BUSY_PIN) == 1:
            time.sleep(10 / 1000.0)

        log(DEBUG, "E-ink screen ready")

        return

    def __turn_on_display__(self):

        log(DEBUG, "Turning full display on")

        # DISPLAY_UPDATE_CONTROL_2
        self.__send_command__(0x22)
        self.__send_data__   (0xF7)

        # MASTER_ACTIVATION
        self.__send_command__(0x20)
        self.__read_busy__   ()

        return

    def __turn_on_display_partial__(self):

        log(DEBUG, "Turning partial display on")

        # DISPLAY_UPDATE_CONTROL_2
        self.__send_command__(0x22)
        self.__send_data__   (0x0F)

        # MASTER_ACTIVATION
        self.__send_command__(0x20)
        self.__read_busy__   ()

        return

    def __set_window__(self, x_start, y_start, x_end, y_end):

        log(DEBUG, "Setting window : {}/{} -> {}/{}".format(x_start, y_start, x_end, y_end))

        # SET_RAM_X_ADDRESS_START_END_POSITION
        self.__send_command__(0x44)
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.__send_data__((x_start >> 3) & 0xFF)
        self.__send_data__((x_end   >> 3) & 0xFF)

        # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.__send_command__(0x45)
        self.__send_data__   ( y_start & 0xFF)
        self.__send_data__   ((y_start >> 8) & 0xFF)
        self.__send_data__   ( y_end   & 0xFF)
        self.__send_data__   ((y_end   >> 8) & 0xFF)

        return

    def __set_cursor__(self, x, y):

        log(DEBUG, "Setting cursor : {}/{}".format(x, y))

        # SET_RAM_X_ADDRESS_COUNTER
        self.__send_command__(0x4E)
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.__send_data__(x & 0xFF)

        # SET_RAM_Y_ADDRESS_COUNTER
        self.__send_command__(0x4F)
        self.__send_data__   ( y & 0xFF)
        self.__send_data__   ((y >> 8) & 0xFF)

        return

    @staticmethod
    def __get_buffer__(image):

        log(DEBUG, 'Getting image buffer')

        buffer = [0xFF] * (int(E_INK_SCREEN_WIDTH / 8) * E_INK_SCREEN_HEIGHT)

        image_monocolor = image.convert('1')
        image_width, image_height = image_monocolor.size
        pixels = image_monocolor.load()

        if image_width == E_INK_SCREEN_WIDTH and image_height == E_INK_SCREEN_HEIGHT:

            log(DEBUG, "Drawing in portrait mode")

            for y in range(image_height):
                for x in range(image_width):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buffer[int((x + y * E_INK_SCREEN_WIDTH) / 8)] &= ~(0x80 >> (x % 8))

        elif image_width == E_INK_SCREEN_HEIGHT and image_height == E_INK_SCREEN_WIDTH:

            log(DEBUG, "Drawing in landscape mode")

            for y in range(image_height):
                for x in range(image_width):
                    new_x = y
                    new_y = E_INK_SCREEN_HEIGHT - x - 1
                    if pixels[x, y] == 0:
                        buffer[int((new_x + new_y * E_INK_SCREEN_WIDTH) / 8)] &= ~(0x80 >> (y % 8))
        return buffer

    def module_init(self):

        log(INFO, 'Resetting E-ink screen module')

        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setwarnings(False)
        RPi.GPIO.setup(E_INK_SCREEN_RESET_PIN, RPi.GPIO.OUT)
        RPi.GPIO.setup(E_INK_SCREEN_DC_PIN   , RPi.GPIO.OUT)
        RPi.GPIO.setup(E_INK_SCREEN_CS_PIN   , RPi.GPIO.OUT)
        RPi.GPIO.setup(E_INK_SCREEN_BUSY_PIN , RPi.GPIO.IN )

        # Hardware reset
        RPi.GPIO.output(E_INK_SCREEN_RESET_PIN, 1)
        time.sleep(10 / 1000.0)
        RPi.GPIO.output(E_INK_SCREEN_RESET_PIN, 0)
        time.sleep(10 / 1000.0)
        RPi.GPIO.output(E_INK_SCREEN_RESET_PIN, 1)
        time.sleep(10 / 1000.0)
        self.__read_busy__()

        # Software reset
        self.__send_command__(0x12)
        self.__read_busy__()

        # Driver output control
        self.__send_command__(0x01)
        self.__send_data__   (0x27)
        self.__send_data__   (0x01)
        self.__send_data__   (0x00)

        # Data entry mode
        self.__send_command__(0x11)
        self.__send_data__   (0x03)

        self.__set_window__(0, 0, E_INK_SCREEN_WIDTH - 1, E_INK_SCREEN_HEIGHT - 1);

        # Display update control
        self.__send_command__(0x21)
        self.__send_data__   (0x00)
        self.__send_data__   (0x80)

        # Set cursor
        self.__set_cursor__(0, 0)

        # Clear screen
        self.__send_command__(0x24)
        for j in range(0, E_INK_SCREEN_HEIGHT):
            for i in range(0, int(E_INK_SCREEN_WIDTH / 8)):
                self.__send_data__(0xFF)

        self.__turn_on_display__()

        return

    def display(self, image):

        log(INFO, 'Display full image')

        # WRITE_RAM
        self.__send_command__(0x24)

        image_buffer = self.__get_buffer__(image)

        for j in range(0, E_INK_SCREEN_HEIGHT):
            for i in range(0, int(E_INK_SCREEN_WIDTH / 8)):
                self.__send_data__(image_buffer[i + j * int(E_INK_SCREEN_WIDTH / 8)])

        self.__turn_on_display__()

        return

    def display_base(self, image):

        log(INFO, 'Display base image')

        # WRITE_RAM
        self.__send_command__(0x24)

        image_buffer = self.__get_buffer__(image)

        for j in range(0, E_INK_SCREEN_HEIGHT):
            for i in range(0, int(E_INK_SCREEN_WIDTH / 8)):
                self.__send_data__(image_buffer[i + j * int(E_INK_SCREEN_WIDTH / 8)])

        self.__send_command__(0x26)

        for j in range(0, E_INK_SCREEN_HEIGHT):
            for i in range(0, int(E_INK_SCREEN_WIDTH / 8)):
                self.__send_data__(image_buffer[i + j * int(E_INK_SCREEN_WIDTH / 8)])

        self.__turn_on_display__()

        return

    def display_partial(self, image):

        log(INFO, 'Display partial image')

        RPi.GPIO.output(E_INK_SCREEN_RESET_PIN, 0)
        time.sleep(10 / 1000.0)
        RPi.GPIO.output(E_INK_SCREEN_RESET_PIN, 1)
        time.sleep(10 / 1000.0)

        # Sending LUT
        self.__send_command__(0x32)
        for i in range(0, len(self.PARTIAL_DISPLAY_LUT) - 1):
            self.__send_data__(self.PARTIAL_DISPLAY_LUT[i])
        self.__read_busy__()

        # self.__send_command__(0x37);
        # self.__send_data__   (0x00);
        # self.__send_data__   (0x00);
        # self.__send_data__   (0x00);
        # self.__send_data__   (0x00);
        # self.__send_data__   (0x00);
        # self.__send_data__   (0x40);
        # self.__send_data__   (0x00);
        # self.__send_data__   (0x00);
        # self.__send_data__   (0x00);
        # self.__send_data__   (0x00);

        # BorderWavefrom
        # self.__send_command__(0x3C);
        # self.__send_data__   (0x80);

        # DISPLAY_UPDATE_CONTROL_2
        self.__send_command__(0x22);
        self.__send_data__   (0xC0);

        # MASTER_ACTIVATION
        self.__send_command__(0x20);
        self.__read_busy__   ();

        #self.__set_window__(0, 0, E_INK_SCREEN_WIDTH - 1, E_INK_SCREEN_HEIGHT - 1)
        #self.__set_cursor__(0, 0)

        # WRITE_RAM
        self.__send_command__(0x24)

        image_buffer = self.__get_buffer__(image)

        for j in range(0, E_INK_SCREEN_HEIGHT):
            for i in range(0, int(E_INK_SCREEN_WIDTH / 8)):
                self.__send_data__(image_buffer[i + j * int(E_INK_SCREEN_WIDTH / 8)])

        self.__turn_on_display_partial__()

        return

    def display_partial2(self, image):

        log(INFO, 'Display partial image')


        # Sending LUT
        self.__send_command__(0x32)
        for i in range(0, len(self.PARTIAL_DISPLAY_LUT) - 1):
            self.__send_data__(self.PARTIAL_DISPLAY_LUT[i])
        self.__read_busy__()

        # DISPLAY_UPDATE_CONTROL_2
        self.__send_command__(0x22);
        self.__send_data__   (0xC0);

        # MASTER_ACTIVATION
        self.__send_command__(0x20);
        self.__read_busy__   ();

        # Clear screen
        self.__send_command__(0x24)
        for j in range(0, E_INK_SCREEN_HEIGHT):
            for i in range(0, int(E_INK_SCREEN_WIDTH / 8)):
                self.__send_data__(0xFF)

        self.__turn_on_display_partial__()

        # Sending LUT
        self.__send_command__(0x32)
        for i in range(0, len(self.PARTIAL_DISPLAY_LUT) - 1):
            self.__send_data__(self.PARTIAL_DISPLAY_LUT[i])
        self.__read_busy__()

        # DISPLAY_UPDATE_CONTROL_2
        self.__send_command__(0x22);
        self.__send_data__   (0xC0);

        # MASTER_ACTIVATION
        self.__send_command__(0x20);
        self.__read_busy__   ();

        image_buffer = self.__get_buffer__(image)

        for j in range(0, E_INK_SCREEN_HEIGHT):
            for i in range(0, int(E_INK_SCREEN_WIDTH / 8)):
                self.__send_data__(image_buffer[i + j * int(E_INK_SCREEN_WIDTH / 8)])

        self.__turn_on_display_partial__()

        return

    def module_exit(self):

        log(INFO, 'Shutting down up E-ink screen')

        # Entering DEEP_SLEEP_MODE
        self.__send_command__(0x10)
        self.__send_data__   (0x01)

        self.spi_device.close()

        RPi.GPIO.output(E_INK_SCREEN_RESET_PIN, 0)
        RPi.GPIO.output(E_INK_SCREEN_DC_PIN   , 0)

        RPi.GPIO.cleanup()

        return
