import RPi.GPIO
import gpiozero
import pigpio

from globals import *
from log     import *

"""
Decode a rotary encoder (button or motor), with an optional switch, e.g. a KY-40.

             +---------+         +---------+      0
             |         |         |         |
   1         |         |         |         |
             |         |         |         |
   +---------+         +---------+         +----- 1

       +---------+         +---------+            0
       |         |         |         |
   2   |         |         |         |
       |         |         |         |
   ----+         +---------+         +---------+  1
"""


class Encoder:

    BOUNCE_TIME = 2

    def __init__(self, name, gpio_interface, encoder_pin_1, encoder_pin_2, encoder_pin_press):

        log(INFO, 'Setting up {} encoder: {} / {} / {}'.format(name, encoder_pin_1, encoder_pin_2, encoder_pin_press))

        self.name              = name
        self.gpio_interface    = gpio_interface
        self.encoder_pin_1     = encoder_pin_1
        self.encoder_pin_2     = encoder_pin_2
        self.encoder_pin_press = encoder_pin_press

        if self.gpio_interface == USE_RPI_GPIO:

            RPi.GPIO.setmode(RPi.GPIO.BCM)
            RPi.GPIO.setwarnings(False)

            RPi.GPIO.setup(encoder_pin_1, RPi.GPIO.IN)
            RPi.GPIO.setup(encoder_pin_2, RPi.GPIO.IN)
            if self.encoder_pin_press is not None:
                RPi.GPIO.setup(encoder_pin_press, RPi.GPIO.IN)

            RPi.GPIO.setup(encoder_pin_1, RPi.GPIO.IN, RPi.GPIO.PUD_UP)
            RPi.GPIO.setup(encoder_pin_2, RPi.GPIO.IN, RPi.GPIO.PUD_UP)
            if self.encoder_pin_press is not None:
                RPi.GPIO.setup(encoder_pin_press, RPi.GPIO.IN, RPi.GPIO.PUD_UP)

            RPi.GPIO.add_event_detect(encoder_pin_1, RPi.GPIO.FALLING, callback = self.callback, bouncetime = self.BOUNCE_TIME)

        elif self.gpio_interface == USE_RPI_ZERO:

            self.encoder_pin_1_device     = gpiozero.DigitalInputDevice(encoder_pin_1, pull_up = True, bounce_time = self.BOUNCE_TIME / 1000)
            self.encoder_pin_2_device     = gpiozero.DigitalInputDevice(encoder_pin_2, pull_up = True, bounce_time = self.BOUNCE_TIME / 1000)
            if self.encoder_pin_press is not None:
                self.encoder_pin_press_device = gpiozero.DigitalInputDevice(encoder_pin_press, pull_up = True, bounce_time = self.BOUNCE_TIME / 1000)

            self.encoder_pin_1_device.when_deactivated = self.callback

        elif self.gpio_interface == USE_PI_GPIO:

            self.level_encoder_1 = 0
            self.level_encoder_2 = 0
            self.last_event_gpio = None

            self.pigpio = pigpio.pi()

            self.pigpio.set_mode(encoder_pin_1, pigpio.INPUT)
            self.pigpio.set_mode(encoder_pin_2, pigpio.INPUT)
            if self.encoder_pin_press is not None:
                self.pigpio.set_mode(encoder_pin_press, pigpio.INPUT)

            self.pigpio.set_pull_up_down(encoder_pin_1, pigpio.PUD_UP)
            self.pigpio.set_pull_up_down(encoder_pin_2, pigpio.PUD_UP)
            if self.encoder_pin_press is not None:
                self.pigpio.set_pull_up_down(encoder_pin_press, pigpio.PUD_UP)

            self.pigpio.callback(encoder_pin_1, pigpio.EITHER_EDGE, self.callback2)
            self.pigpio.callback(encoder_pin_2, pigpio.EITHER_EDGE, self.callback2)

        self.counter = 0

        return

    def callback(self, channel):

        if self.gpio_interface == USE_RPI_GPIO:

            pin_1_state = RPi.GPIO.input(self.encoder_pin_1)
            pin_2_state = RPi.GPIO.input(self.encoder_pin_2)

        elif self.gpio_interface == USE_RPI_ZERO:

            pin_1_state = self.encoder_pin_1_device.value
            pin_2_state = self.encoder_pin_2_device.value

        if pin_1_state != pin_2_state:
            self.counter += 1
        else:
            self.counter -= 1

        log(DEBUG, '{} encoder callback 1: pin_1_state - {} / pin_2_state - {} / counter - {}'.format(self.name, pin_1_state, pin_2_state, self.counter))

        return

    def callback2(self, gpio, level, tick):

        if gpio == self.encoder_pin_1:
            self.level_encoder_1 = level
        else:
            self.level_encoder_2 = level

        if gpio != self.last_event_gpio:

            self.last_event_gpio = gpio

            if gpio == self.encoder_pin_1 and level == 1:

                if self.level_encoder_2 == 1:
                    self.counter -= 1

            elif gpio == self.encoder_pin_2 and level == 1:

                if self.level_encoder_1 == 1:
                    self.counter += 1

        log(DEBUG, '{} encoder callback 1: level_encoder_1 - {} / level_encoder_2 - {} / counter - {}'.format(self.name, self.level_encoder_1, self.level_encoder_2, self.counter))

        return

    def get_counter(self):

        return self.counter

    def reset_counter(self):

        log(DEBUG, '{} encoder counter reset'.format(self.name))

        self.counter = 0

        return

    def is_pressed(self):

        if self.encoder_pin_press is None:

            log(WARNING, '{} encoder not setup with a press pin'.format(self.name))

            return False

        else:

            if self.gpio_interface == USE_RPI_GPIO:

                pin_press_state = RPi.GPIO.input(self.encoder_pin_press)

            elif self.gpio_interface == USE_RPI_ZERO:

                pin_press_state = self.encoder_pin_press_device.value

            elif self.gpio_interface == USE_PI_GPIO:

                pin_press_state = self.pigpio.read(self.encoder_pin_press)

            if pin_press_state == 0:
                return False
            else:
                log(DEBUG, '{} encoder\'s button pressed'.format(self.name))
                return True
