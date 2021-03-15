import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont

sys.path.append("..")

import einkscreen

from optparse import OptionParser
from log      import *

VERSION          = '1.0'
UPDATE_DATE      = '2021-03-05'
VERSION_STRING   = '%%prog v%s (%s)' % (VERSION, UPDATE_DATE)
USAGE            = 'usage: %prog [-h] [--verbose=INT] --spi-address=INT [--draw-portrait] [--draw-landscape] [--draw-full-bmp] [--draw-window-bmp] [--draw-partial-update]'
LONG_DESCRIPTION = 'This program makes possible to easily test the E-ink screen class. ' \
                   'Verbose level is between 0 (lowest) & 4.'

# Default log level
DEFAULT_LOG_LEVEL = DEBUG

# Minimum required version of Python interpreter
REQUIRED_PYTHON_VERSION = 3

# Other constants
SPI_BUS_NUMBER      = 0
E_INK_SCREEN_WIDTH  = 128
E_INK_SCREEN_HEIGHT = 296

# Global variables
e_ink_screen = None


def main():

    global e_ink_screen

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

        parser.add_option('-s',
                          '--spi-address',
                          action  = 'store',
                          dest    = 'spi_address',
                          help    = 'Mandatory - Set the E-Ink Screen\'s SPI address (e.g. 0)',
                          metavar = 'INT')

        parser.add_option('-p',
                          '--draw-portrait',
                          action  = 'store_true',
                          dest    = 'draw_portrait',
                          help    = 'Optional - Test drawing in portrait mode')

        parser.add_option('-l',
                          '--draw-landscape',
                          action  = 'store_true',
                          dest    = 'draw_landscape',
                          help    = 'Optional - Test drawing in landscape mode')

        parser.add_option('-b',
                          '--draw-full-bmp',
                          action  = 'store_true',
                          dest    = 'draw_full_bmp',
                          help    = 'Optional - Test drawing with bitmap image in full screen')

        parser.add_option('-w',
                          '--draw-window-bmp',
                          action  = 'store_true',
                          dest    = 'draw_window_bmp',
                          help    = 'Optional - Test drawing with bitmap image in a window')

        parser.add_option('-u',
                          '--draw-partial-update',
                          action  = 'store_true',
                          dest    = 'draw_partial_update',
                          help    = 'Optional - Test drawing with partial update')

        # Set options defaults
        parser.set_defaults(verbose = DEFAULT_LOG_LEVEL)

        # Actually process input options
        try:
            (opts, args) = parser.parse_args(argv)
        except SystemExit:
            return 3

        # Check the retrieved options, if any
        if not opts.spi_address:
            log(ERROR , 'Missing input mandatory option --spi-address. Try --help')
            return 3

        log_set_level(int(opts.verbose))

    except Exception as error:
        log(ERROR, 'Unexpected parsing error. Try --help')
        log(ERROR, '{}'.format(error))
        return 3

    # Options are OK: process with the test
    os.system('clear')

    log(INFO, '***********************************')
    log(INFO, '* Starting E-Ink Class testing... *')
    log(INFO, '***********************************')
    log(INFO, '')
    log(INFO, 'Initiating...')
    log(INFO, '')

    e_ink_screen = einkscreen.EInkScreen(SPI_BUS_NUMBER, int(opts.spi_address))

    e_ink_screen.module_init()

    font14 = ImageFont.truetype('e_ink_screen_font.ttc', 14)
    font18 = ImageFont.truetype('e_ink_screen_font.ttc', 18)
    font24 = ImageFont.truetype('e_ink_screen_font.ttc', 24)

    if opts.draw_landscape == True:

        log(INFO, "Drawing image with landscape orientation")

        draw_image = Image.new('1', (E_INK_SCREEN_HEIGHT, E_INK_SCREEN_WIDTH), 255)
        drawer     = ImageDraw.Draw(draw_image)

        drawer.text(( 10,  0), 'Hello world'    , font = font24, fill = 0)
        drawer.text(( 10, 20), '2.9inch e-Paper', font = font24, fill = 0)
        drawer.text((150,  0), 'Smaller text'   , font = font18, fill = 0)

        drawer.line     ((20, 50, 70, 100), fill    = 0)
        drawer.line     ((70, 50, 20, 100), fill    = 0)
        drawer.rectangle((20, 50, 70, 100), outline = 0)

        drawer.line((165, 50, 165, 100),         fill = 0)
        drawer.line((140, 75, 190,  75),         fill = 0)
        drawer.arc ((140, 50, 190, 100), 0, 360, fill = 0)

        drawer.rectangle((80, 50, 130, 100), fill = 0)

        drawer.chord((200, 50, 250, 100), 0, 360, fill = 0)

        e_ink_screen.display(draw_image)

        time.sleep(3)

    if opts.draw_portrait == True:

        log(INFO, "Drawing image with portrait orientation")

        draw_image = Image.new('1', (E_INK_SCREEN_WIDTH, E_INK_SCREEN_HEIGHT), 255)
        drawer      = ImageDraw.Draw(draw_image)

        drawer.text(( 2,  0), 'Hello world' , font = font18, fill = 0)
        drawer.text(( 2, 20), '2.9inch EPD' , font = font18, fill = 0)
        drawer.text((20, 50), 'Smaller text', font = font14, fill = 0)

        drawer.line     ((10, 90, 60, 140), fill    = 0)
        drawer.line     ((60, 90, 10, 140), fill    = 0)
        drawer.rectangle((10, 90, 60, 140), outline = 0)

        drawer.line((95,  90,  95, 140),         fill = 0)
        drawer.line((70, 115, 120, 115),         fill = 0)
        drawer.arc ((70,  90, 120, 140), 0, 360, fill = 0)

        drawer.rectangle((10, 150, 60, 200), fill = 0)

        drawer.chord((70, 150, 120, 200), 0, 360, fill = 0)

        e_ink_screen.display(draw_image)

        time.sleep(3)

    if opts.draw_full_bmp == True:

        log(INFO, "Drawing with a full screen bitmap image")

        bmp_image = Image.open('e_ink_screen_full.bmp')
        e_ink_screen.display(bmp_image)
        time.sleep(3)

    if opts.draw_window_bmp == True:

        log(INFO, "Drawing with a window bitmap image")

        bmp_image  = Image.new('1', (E_INK_SCREEN_HEIGHT, E_INK_SCREEN_WIDTH), 255)
        bmp_window = Image.open('e_ink_screen_window_2.bmp')
        bmp_image.paste(bmp_window, (50, 10))
        e_ink_screen.display(bmp_image)
        time.sleep(3)

    if opts.draw_partial_update == True:

        log(INFO, "Drawing with partial update")

        base_image = Image.new('1', (E_INK_SCREEN_HEIGHT, E_INK_SCREEN_WIDTH), 255)
        drawer     = ImageDraw.Draw(base_image)

        e_ink_screen.display_base(base_image)

        num = 0

        while True:

            drawer.rectangle((10, 10, 120, 50), fill = 255)
            drawer.text     ((10, 10), time.strftime('%H:%M:%S'), font = font24, fill = 0)
            e_ink_screen.display_partial(base_image)

            num = num + 1
            if num == 5:
                break

    log(INFO, '')
    log(INFO, 'Exiting...')
    log(INFO, '')
    log(INFO, '************************************')
    log(INFO, '* Done with E-Ink Class testing... *')
    log(INFO, '************************************')

    return 0


def graceful_exit(return_code):

    global e_ink_screen

    if e_ink_screen is not None:

        e_ink_screen.module_init()
        e_ink_screen.module_exit()

    os._exit(return_code)

    return


if __name__ == '__main__':

    try:

        log_init(ERROR)

        main_status = main()

        graceful_exit(main_status)

    except KeyboardInterrupt:
        log(ERROR, 'Keyboard interrupt...')
        graceful_exit(1)

    except Exception as error:
        log(ERROR, 'Error: ' + str(error))
        graceful_exit(2)
