import os
import sys
import time
import threading

sys.path.append("..")

import rotarybutton

from optparse import OptionParser
from globals  import *
from log      import *

BUTTON_TEST_STATES   = ['MODE_1', 'MODE_2', 'MODE_3', 'MODE_4', 'MODE_5']
BUTTON_TEST_LOOP     = False
BUTTON_DEFAULT_STATE = 'MODE_3'

VERSION          = '1.0'
UPDATE_DATE      = '2021-01-28'
VERSION_STRING   = '%%prog v%s (%s)' % (VERSION, UPDATE_DATE)
USAGE            = 'usage: %prog [-h] [--verbose=INT] --input-pin-1=INT --input-pin-2=INT --input-pin-press=INT'
LONG_DESCRIPTION = 'This program makes possible to easily test a KY-40 rotary encoder with Python. ' \
                   'Pin numbers refers to BCM numbering. Verbose level is between 0 (lowest) & 4.'

# Default log level
DEFAULT_LOG_LEVEL = DEBUG

# Minimum required version of Python interpreter
REQUIRED_PYTHON_VERSION = 3

# Supported commands
EMPTY_COMMAND = ''
QUIT_COMMAND  = 'q'

# Global variables
user_input_string = EMPTY_COMMAND
quit_input_thread = False


def user_input_thread():

    global user_input_string
    global quit_input_thread

    log(DEBUG, 'Starting user input thread')

    while quit_input_thread == False:

        user_input_string = input()

    log(DEBUG, 'Leaving user input thread')

    return


def main():

    global user_input_string

    # Get input options
    argv = sys.argv[1:]

    # Check python version is the minimum expected one
    if sys.version_info[0] < REQUIRED_PYTHON_VERSION:

        log(ERROR, 'This tool requires at least Python version {}'.format(REQUIRED_PYTHON_VERSION))
        sys.exit(3)

    # Setup options parser
    try:
        parser = OptionParser(usage   = USAGE,
                              version = VERSION_STRING,
                              epilog  = LONG_DESCRIPTION)

        parser.add_option('-v',
                          '--verbose',
                          action  = 'store',
                          dest    = 'verbose',
                          help    = 'Optional - Set verbose level [default: %default]',
                          metavar = 'INT')

        parser.add_option('-1',
                          '--input-pin-1',
                          action  = 'store',
                          dest    = 'input_pin_1',
                          help    = 'Mandatory - Set the encoder\'s pin #1 (a.k.a. CLK or DT)',
                          metavar = 'INT')

        parser.add_option('-2',
                          '--input-pin-2',
                          action  = 'store',
                          dest    = 'input_pin_2',
                          help    = 'Mandatory - Set the encoder\'s pin #2 (a.k.a. DT or CLK)',
                          metavar = 'INT')

        parser.add_option('-3',
                          '--input-pin-press',
                          action  = 'store',
                          dest    = 'input_pin_press',
                          help    = 'Mandatory - Set the button\'s press pin (a.k.a. SW)',
                          metavar = 'INT')

        # Set options defaults
        parser.set_defaults(verbose = DEFAULT_LOG_LEVEL)

        # Actually process input options
        try:
            (opts, args) = parser.parse_args(argv)
        except SystemExit:
            return 3

        # Check the retrieved options, if any
        if not opts.input_pin_1:
            log(ERROR , 'Missing input mandatory option --input-pin-1. Try --help')
            return 3

        if not opts.input_pin_2:
            log(ERROR, 'Missing input mandatory option --input-pin-2. Try --help')
            return 3

        if not opts.input_pin_press:
            log(ERROR, 'Missing input mandatory option --input-pin-press. Try --help')
            return 3

        log_set_level(int(opts.verbose))

    except Exception as error:
        log(ERROR, 'Unexpected parsing error. Try --help')
        log(ERROR, '{}'.format(error))
        return 3

    # Options are OK: process with the test
    os.system('clear')

    log(INFO, '********************************************')
    log(INFO, '* Starting Rotary States Button testing... *')
    log(INFO, '********************************************')
    log(INFO, '')
    log(INFO, 'Type "{}" to quit test'.format(QUIT_COMMAND))
    log(INFO, '')

    button = rotarybutton.RotaryStatesButton('TEST_BUTTON', USE_RPI_ZERO, opts.input_pin_1, opts.input_pin_2, opts.input_pin_press, BUTTON_TEST_STATES, BUTTON_TEST_LOOP)

    button.set_state(BUTTON_DEFAULT_STATE)

    last_state        = ''
    last_value        = 0
    last_press_status = False
    last_command      = user_input_string

    while True:

        current_state = button.get_state()
        current_value = button.get_value()

        if (current_state != last_state) or (current_value != last_value):
            log(INFO, 'Current state / value: {} / {}'.format(current_state, current_value))
            last_state = current_state
            last_value = current_value

        current_press_status = button.is_pressed()

        if current_press_status != last_press_status:

            if current_press_status == True:
                log(INFO, 'Button currently being pressed')
            else:
                log(INFO, 'Button currently being released')

            last_press_status = current_press_status

        current_click_status = button.was_clicked()

        if current_click_status == True:
            log(INFO, 'Button was just clicked')

        if user_input_string == QUIT_COMMAND:

            log(INFO, 'Exiting!')
            log(INFO, '')
            log(INFO, '*********************************************')
            log(INFO, '* Done with Rotary States Button testing... *')
            log(INFO, '*********************************************')

            return 0

        elif user_input_string != last_command and user_input_string != EMPTY_COMMAND:

            log(WARNING, 'Unsupported command: "{}"'.format(user_input_string))
            last_command = user_input_string

        time.sleep(0.01)

    return


def graceful_exit(return_code):

    # Cleanup GPIOs if button is created with USE_RPI_GPIO
    # RPi.GPIO.cleanup()

    os._exit(return_code)

    return


if __name__ == '__main__':

    try:

        log_init(ERROR)

        input_thread = threading.Thread(target = user_input_thread, name = 'user-input-thread', args = [])
        input_thread.start()

        main_status = main()

        quit_input_thread = True

        input_thread.join()

        graceful_exit(main_status)

    except KeyboardInterrupt:
        log(ERROR, 'Keyboard interrupt...')
        graceful_exit(1)

    except Exception as error:
        log(ERROR, 'Error: ' + str(error))
        graceful_exit(2)
