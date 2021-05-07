#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

test_pin = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(test_pin, GPIO.OUT)

for i in range(10):
    GPIO.output(test_pin, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(test_pin, GPIO.LOW)
    time.sleep(0.9)

GPIO.cleanup()