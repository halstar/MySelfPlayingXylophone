import os
import sys
import time
import threading

sys.path.append("..")

import ioextender

from optparse import OptionParser
from log      import *

VERSION          = '1.0'
UPDATE_DATE      = '2021-02-03'
VERSION_STRING   = '%%prog v%s (%s)' % (VERSION, UPDATE_DATE)
USAGE            = 'usage: %prog [-h] [--verbose=INT] --input-pin-1=INT --input-pin-2=INT --input-pin-press=INT'
LONG_DESCRIPTION = 'This program makes possible to easily test the IO extender class.\n' \
                   'This refers to MCP 23017 chip. Verbose level is between 0 (lowest) & 4.'

# Default log level
DEFAULT_LOG_LEVEL = DEBUG

# Minimum required version of Python interpreter
REQUIRED_PYTHON_VERSION = 3

# Supported commands
EMPTY_COMMAND = ''
QUIT_COMMAND  = 'q'

# Other constants
I2C_BUS_NUMBER = 1

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

        parser.add_option('-i',
                          '--i2c-address',
                          action  = 'store',
                          dest    = 'i2c_address',
                          help    = 'Mandatory - Set the IO extender\'s I2C address (e.g. 32 for 0x20)',
                          metavar = 'INT')

        parser.add_option('-p',
                          '--primary-io-pin',
                          action  = 'store',
                          dest    = 'primary_io_pin',
                          help    = 'Mandatory - Primary IO pin to test (0 to 31)',
                          metavar = 'INT')

        parser.add_option('-s',
                          '--secondary-io-pin',
                          action  = 'store',
                          dest    = 'secondary_io_pin',
                          help    = 'Optional - Secondray IO pin to test (0 to 31)',
                          metavar = 'INT')

        parser.add_option('-0',
                          '--low-level-duration',
                          action  = 'store',
                          dest    = 'low_level_duration',
                          help    = 'Mandatory - Duration of the low level state, in milliseconds',
                          metavar = 'INT')

        parser.add_option('-1',
                          '--high-level-duration',
                          action  = 'store',
                          dest    = 'high_level_duration',
                          help    = 'Mandatory - Duration of the high level state, in milliseconds',
                          metavar = 'INT')

        # Set options defaults
        parser.set_defaults(verbose = DEFAULT_LOG_LEVEL)

        # Actually process input options
        try:
            (opts, args) = parser.parse_args(argv)
        except SystemExit:
            return 3

        # Check the retrieved options, if any
        if not opts.i2c_address:
            log(ERROR , 'Missing input mandatory option --i2c-address. Try --help')
            return 3

        if not opts.primary_io_pin:
            log(ERROR, 'Missing input mandatory option --primary-io-pin. Try --help')
            return 3

        if opts.secondary_io_pin and opts.primary_io_pin == opts.secondary_io_pin:
            log(ERROR, '--primary-io-pin & --secondary-io-pin shall be different. Try --help')
            return 3

        if not opts.low_level_duration:
            log(ERROR, 'Missing input mandatory option --low-level-duration. Try --help')
            return 3

        if not opts.high_level_duration:
            log(ERROR, 'Missing input mandatory option --high-level-duration. Try --help')
            return 3

        log_set_level(int(opts.verbose))

    except Exception as error:
        log(ERROR, 'Unexpected parsing error. Try --help')
        log(ERROR, '{}'.format(error))
        return 3

    # Options are OK: process with the test
    os.system('clear')

    log(INFO, '*****************************************')
    log(INFO, '* Starting IO Extender Class testing... *')
    log(INFO, '*****************************************')
    log(INFO, '')
    log(INFO, 'Type "{}" to quit test'.format(QUIT_COMMAND))
    log(INFO, '')

    io_extender = ioextender.IoExtender(I2C_BUS_NUMBER, int(opts.i2c_address))

    last_command = user_input_string

    if not opts.secondary_io_pin:
        test_io = int(opts.primary_io_pin)
    else:
        test_ios_values_low = [{'pin' : int(opts.primary_io_pin  ), 'value' : 0},
                               {'pin' : int(opts.secondary_io_pin), 'value' : 0}]

        test_ios_values_high = [{'pin' : int(opts.primary_io_pin  ), 'value' : 1},
                                {'pin' : int(opts.secondary_io_pin), 'value' : 1}]

    while True:

        log(DEBUG, 'Test toggling IO(s) high')

        if not opts.secondary_io_pin:
            io_extender.write_io(test_io, 1)
        else:
            io_extender.write_ios(test_ios_values_high)

        time.sleep(int(opts.high_level_duration) / 1000.0)

        log(DEBUG, 'Test toggling IO(s) low')

        if not opts.secondary_io_pin:
            io_extender.write_io(test_io, 0)
        else:
            io_extender.write_ios(test_ios_values_low)

        time.sleep(int(opts.low_level_duration) / 1000.0)

        if user_input_string == QUIT_COMMAND:

            log(INFO, 'Exiting!')
            log(INFO, '')
            log(INFO, '******************************************')
            log(INFO, '* Done with IO Extender Class testing... *')
            log(INFO, '******************************************')

            return 0

        elif user_input_string != last_command and user_input_string != EMPTY_COMMAND:

            log(WARNING, 'Unsupported command: "{}"'.format(user_input_string))
            last_command = user_input_string


if __name__ == '__main__':

    try:

        log_init(ERROR)

        input_thread = threading.Thread(target = user_input_thread, name = 'user-input-thread', args = [])
        input_thread.start()

        main_status = main()

        quit_input_thread = True

        input_thread.join()

        os._exit(main_status)

    except KeyboardInterrupt:
        log(ERROR, 'Keyboard interrupt...')
        os._exit(1)

    except Exception as error:
        log(ERROR, 'Error: ' + str(error))
        os._exit(2)
