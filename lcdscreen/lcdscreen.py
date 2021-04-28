import threading
import time
import RPi.GPIO
import gpiozero
import pigpio
import spi
import numpy

from PIL import Image

from log     import *
from globals import *


class LcdScreen:

    SPI_MAX_SPEED_IN_HZ = 40000000

    def __init__(self, gpio_interface, bus, address):

        log(INFO, 'Setting up LCD screen class')

        self.gpio_interface      = gpio_interface
        self.spi_device          = spi.SpiDevice(bus, address, self.SPI_MAX_SPEED_IN_HZ)
        self.is_init_in_progress = False

        return

    def __output_gpio__(self, gpio, value):

        if self.gpio_interface == USE_RPI_GPIO:

            RPi.GPIO.output(gpio, value)

        elif self.gpio_interface == USE_RPI_ZERO:

            if gpio == LCD_SCREEN_RESET_PIN:
                self.pin_reset.value = value
            elif gpio == LCD_SCREEN_DC_PIN:
                self.pin_dc.value = value
            elif gpio == LCD_SCREEN_CS_PIN:
                self.pin_cs.value = value
            elif gpio == LCD_SCREEN_BL_PIN:
                self.pin_bl.value = value

        elif self.gpio_interface == USE_PI_GPIO:

            self.pigpio.write(gpio, value)

    def __send_command__(self, command):

        log(DEBUG, "Sending command: 0x{:02X}".format(command))

        self.__output_gpio__(LCD_SCREEN_DC_PIN, 0)
        self.__output_gpio__(LCD_SCREEN_CS_PIN, 0)
        self.spi_device.write_bytes([command]    )
        self.__output_gpio__(LCD_SCREEN_CS_PIN, 1)

        return

    def __send_data_list__(self, data_list):

        # No log while sending data or console would be flooded

        self.__output_gpio__(LCD_SCREEN_DC_PIN, 1)
        self.__output_gpio__(LCD_SCREEN_CS_PIN, 0)
        self.spi_device.write_bytes(data_list    )
        self.__output_gpio__(LCD_SCREEN_CS_PIN, 1)

    def __send_data__(self, data):

        # No log while sending data or console would be flooded

        self.__output_gpio__(LCD_SCREEN_DC_PIN, 1)
        self.__output_gpio__(LCD_SCREEN_CS_PIN, 0)
        self.spi_device.write_bytes([data]       )
        self.__output_gpio__(LCD_SCREEN_CS_PIN, 1)

        return

    def __set_window__(self, x_start, y_start, x_end, y_end):

        log(DEBUG, "Setting window : {}/{} -> {}/{}".format(x_start, y_start, x_end, y_end))

        # Set the X coordinates
        self.__send_command__(0x2A)
        self.__send_data__   ( x_start >> 8)      # Set the horizontal starting point to the high octet
        self.__send_data__   ( x_start & 0xFF)    # Set the horizontal starting point to the low octet
        self.__send_data__   ( x_end   >> 8)      # Set the horizontal end to the high octet
        self.__send_data__   ((x_end - 1) & 0xFF) # Set the horizontal end to the low octet 

        # Set the Y coordinates
        self.__send_command__(0x2B)
        self.__send_data__   ( y_start >> 8)
        self.__send_data__   ( y_start & 0xFF)
        self.__send_data__   ( y_end >> 8)
        self.__send_data__   ((y_end - 1) & 0xFF)

        self.__send_command__(0x2C)

        return

    def display(self, image):

        log(DEBUG, 'Display image on LCD')

        image_width, image_height = image.size
        
        if (image_width == LCD_SCREEN_HEIGHT) and (image_height == LCD_SCREEN_WIDTH):

            log(DEBUG, "Drawing in landscape mode")

            img = numpy.asarray(image)
            pix = numpy.zeros((LCD_SCREEN_WIDTH, LCD_SCREEN_HEIGHT, 2), dtype = numpy.uint8)
            
            # RGB888 >> RGB565
            pix[..., [0]] = numpy.add(numpy.bitwise_and(img[..., [0]], 0xF8), numpy.right_shift(img[..., [1]], 5))
            pix[..., [1]] = numpy.add(numpy.bitwise_and(numpy.left_shift(img[..., [1]], 3), 0xE0), numpy.right_shift(img[..., [2]], 3))
            pix = pix.flatten().tolist()

            self.__send_command__(0x36)
            self.__send_data__   (0x78)
            self.__set_window__ (0, 0, LCD_SCREEN_HEIGHT, LCD_SCREEN_WIDTH)

            for i in range(0, len(pix), 4096):
                self.__send_data_list__(pix[i:i + 4096])

        elif (image_width == LCD_SCREEN_WIDTH) and (image_height == LCD_SCREEN_HEIGHT):

            log(DEBUG, "Drawing in portrait mode")

            img = numpy.asarray(image)
            pix = numpy.zeros((image_height, image_width, 2), dtype = numpy.uint8)

            # RGB888 >> RGB565
            pix[..., [0]] = numpy.add(numpy.bitwise_and(img[..., [0]], 0xF8), numpy.right_shift(img[..., [1]], 5))
            pix[..., [1]] = numpy.add(numpy.bitwise_and(numpy.left_shift(img[..., [1]], 3), 0xE0), numpy.right_shift(img[..., [2]], 3))

            pix = pix.flatten().tolist()

            self.__send_command__(0x36)
            self.__send_data__   (0x08)
            self.__set_window__ (0, 0, LCD_SCREEN_WIDTH, LCD_SCREEN_HEIGHT)

            for i in range(0, len(pix), 4096):
                self.__send_data_list__(pix[i:i + 4096])

        else:

            log(ERROR, "Cannot display image; bad image size: {}x{}".format(image_width, image_height))

        return

    def module_init(self):

        log(INFO, 'Resetting LCD screen module')

        if self.gpio_interface == USE_RPI_GPIO:

            RPi.GPIO.setmode(RPi.GPIO.BCM)
            RPi.GPIO.setwarnings(False)
            RPi.GPIO.setup(LCD_SCREEN_RESET_PIN, RPi.GPIO.OUT)
            RPi.GPIO.setup(LCD_SCREEN_DC_PIN   , RPi.GPIO.OUT)
            RPi.GPIO.setup(LCD_SCREEN_CS_PIN   , RPi.GPIO.OUT)
            RPi.GPIO.setup(LCD_SCREEN_BL_PIN   , RPi.GPIO.OUT)

        elif self.gpio_interface == USE_RPI_ZERO:

            self.pin_reset = gpiozero.DigitalOutputDevice(LCD_SCREEN_RESET_PIN)
            self.pin_dc    = gpiozero.DigitalOutputDevice(LCD_SCREEN_DC_PIN   )
            self.pin_cs    = gpiozero.DigitalOutputDevice(LCD_SCREEN_CS_PIN   )
            self.pin_bl    = gpiozero.DigitalOutputDevice(LCD_SCREEN_BL_PIN   )

        elif self.gpio_interface == USE_PI_GPIO:

            self.pigpio = pigpio.pi()

            self.pigpio.set_mode(LCD_SCREEN_RESET_PIN, pigpio.OUTPUT)
            self.pigpio.set_mode(LCD_SCREEN_DC_PIN   , pigpio.OUTPUT)
            self.pigpio.set_mode(LCD_SCREEN_CS_PIN   , pigpio.OUTPUT)
            self.pigpio.set_mode(LCD_SCREEN_BL_PIN   , pigpio.OUTPUT)

        # Turn backlight ON by default
        self.__output_gpio__(LCD_SCREEN_BL_PIN, 1)

        # Hardware reset
        self.__output_gpio__(LCD_SCREEN_RESET_PIN, 1)
        time.sleep(10 / 1000.0)
        self.__output_gpio__(LCD_SCREEN_RESET_PIN, 0)
        time.sleep(10 / 1000.0)
        self.__output_gpio__(LCD_SCREEN_RESET_PIN, 1)
        time.sleep(10 / 1000.0)

        # Take device out of sleep
        self.__send_command__(0x11)

        # Setup screen
        self.__send_command__(0xCF)
        self.__send_data__   (0x00)
        self.__send_data__   (0xC1)
        self.__send_data__   (0X30)
        self.__send_command__(0xED)
        self.__send_data__   (0x64)
        self.__send_data__   (0x03)
        self.__send_data__   (0X12)
        self.__send_data__   (0X81)
        self.__send_command__(0xE8)
        self.__send_data__   (0x85)
        self.__send_data__   (0x00)
        self.__send_data__   (0x79)
        self.__send_command__(0xCB)
        self.__send_data__   (0x39)
        self.__send_data__   (0x2C)
        self.__send_data__   (0x00)
        self.__send_data__   (0x34)
        self.__send_data__   (0x02)
        self.__send_command__(0xF7)
        self.__send_data__   (0x20)
        self.__send_command__(0xEA)
        self.__send_data__   (0x00)
        self.__send_data__   (0x00)
        # Power control
        self.__send_command__(0xC0)
        # VRH[5:0]
        self.__send_data__   (0x1D)
        # Power control
        self.__send_command__(0xC1)
        # SAP[2:0] - BT[3:0]
        self.__send_data__   (0x12)
        # VCM control
        self.__send_command__(0xC5)
        self.__send_data__   (0x33)
        self.__send_data__   (0x3F)
        # VCM control
        self.__send_command__(0xC7)
        self.__send_data__   (0x92)
        # Memory access control
        self.__send_command__(0x3A)
        self.__send_data__   (0x55)
        # Memory access control
        self.__send_command__(0x36)
        self.__send_data__   (0x08)
        self.__send_command__(0xB1)
        self.__send_data__   (0x00)
        self.__send_data__   (0x12)
        # Display function control
        self.__send_command__(0xB6)
        self.__send_data__   (0x0A)
        self.__send_data__   (0xA2)
        self.__send_command__(0x44)
        self.__send_data__   (0x02)
        # Gamma function disable
        self.__send_command__(0xF2)
        self.__send_data__   (0x00)
        # Gamma curve selected
        self.__send_command__(0x26)
        self.__send_data__   (0x01)
        # Set gamma
        self.__send_command__(0xE0)
        self.__send_data__   (0x0F)
        self.__send_data__   (0x22)
        self.__send_data__   (0x1C)
        self.__send_data__   (0x1B)
        self.__send_data__   (0x08)
        self.__send_data__   (0x0F)
        self.__send_data__   (0x48)
        self.__send_data__   (0xB8)
        self.__send_data__   (0x34)
        self.__send_data__   (0x05)
        self.__send_data__   (0x0C)
        self.__send_data__   (0x09)
        self.__send_data__   (0x0F)
        self.__send_data__   (0x07)
        self.__send_data__   (0x00)
        # Set gamma
        self.__send_command__(0XE1)
        self.__send_data__   (0x00)
        self.__send_data__   (0x23)
        self.__send_data__   (0x24)
        self.__send_data__   (0x07)
        self.__send_data__   (0x10)
        self.__send_data__   (0x07)
        self.__send_data__   (0x38)
        self.__send_data__   (0x47)
        self.__send_data__   (0x4B)
        self.__send_data__   (0x0A)
        self.__send_data__   (0x13)
        self.__send_data__   (0x06)
        self.__send_data__   (0x30)
        self.__send_data__   (0x38)
        self.__send_data__   (0x0F)
        # Display ON
        self.__send_command__(0x29)

        return

    def __init_animation_thread__(self):

        counter = 0

        image_file_1 = Image.open('display/init_1.png')
        image_file_2 = Image.open('display/init_2.png')
        image_file_3 = Image.open('display/init_3.png')
        image_file_4 = Image.open('display/init_4.png')
        image_file_5 = Image.open('display/init_5.png')
        image_file_6 = Image.open('display/init_6.png')
        image_file_7 = Image.open('display/init_7.png')

        while self.is_init_in_progress == True:

            if counter % 7 == 0:
                self.display(image_file_1)
            elif counter % 7 == 1:
                self.display(image_file_2)
            elif counter % 7 == 2:
                self.display(image_file_3)
            elif counter % 7 == 3:
                self.display(image_file_4)
            elif counter % 7 == 4:
                self.display(image_file_5)
            elif counter % 7 == 5:
                self.display(image_file_6)
            elif counter % 7 == 6:
                self.display(image_file_7)

            counter += 1

            time.sleep(3)

        return

    def start_init_animation(self):

        log(INFO, 'LCD screen starting initialization animation thread')

        self.is_init_in_progress = True

        init_thread = threading.Thread(target = self.__init_animation_thread__, name = 'init_animation', args = [])
        init_thread.start()

        return

    def stop_init_animation(self):

        log(INFO, 'LCD screen stopping initialization animation thread')

        self.is_init_in_progress = False

        return

    def module_exit(self):

        log(INFO, 'Shutting down LCD screen')

        self.spi_device.close()

        self.__output_gpio__(LCD_SCREEN_RESET_PIN, 0)
        self.__output_gpio__(LCD_SCREEN_DC_PIN   , 0)
        self.__output_gpio__(LCD_SCREEN_BL_PIN   , 0)

        return
