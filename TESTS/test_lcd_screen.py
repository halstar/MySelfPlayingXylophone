import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont

sys.path.append("..")

import lcdscreen

from optparse import OptionParser
from log      import *

VERSION          = '1.0'
UPDATE_DATE      = '2021-03-15'
VERSION_STRING   = '%%prog v%s (%s)' % (VERSION, UPDATE_DATE)
USAGE            = 'usage: %prog [-h] [--verbose=INT] --spi-address=INT [--drawer-portrait] [--drawer-landscape] [--drawer-full-bmp] [--drawer-window-bmp] [--drawer-partial-update]'
LONG_DESCRIPTION = 'This program makes possible to easily test the LCD screen class. ' \
                   'Verbose level is between 0 (lowest) & 4.'

# Default log level
DEFAULT_LOG_LEVEL = DEBUG

# Minimum required version of Python interpreter
REQUIRED_PYTHON_VERSION = 3

# Other constants
SPI_BUS_NUMBER      = 0
LCD_SCREEN_WIDTH  = 240
LCD_SCREEN_HEIGHT = 320

# Global variables
lcd_screen = None


def main():

    global lcd_screen

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
                          help    = 'Mandatory - Set the LCD Screen\'s SPI address (e.g. 0)',
                          metavar = 'INT')

        parser.add_option('-p',
                          '--drawer-portrait',
                          action  = 'store_true',
                          dest    = 'draw_portrait',
                          help    = 'Optional - Test drawing in portrait mode')

        parser.add_option('-l',
                          '--drawer-landscape',
                          action  = 'store_true',
                          dest    = 'draw_landscape',
                          help    = 'Optional - Test drawing in landscape mode')

        parser.add_option('-b',
                          '--drawer-full-bmp',
                          action  = 'store_true',
                          dest    = 'draw_full_bmp',
                          help    = 'Optional - Test drawing with bitmap image in full screen')

        parser.add_option('-w',
                          '--drawer-window-bmp',
                          action  = 'store_true',
                          dest    = 'draw_window_bmp',
                          help    = 'Optional - Test drawing with bitmap image in a window')

        parser.add_option('-u',
                          '--drawer-partial-update',
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
    log(INFO, '*  Starting LCD Class testing...  *')
    log(INFO, '***********************************')
    log(INFO, '')
    log(INFO, 'Initiating...')
    log(INFO, '')

    lcd_screen = lcdscreen.LcdScreen(SPI_BUS_NUMBER, int(opts.spi_address))

    lcd_screen.module_init()

    font_1 = ImageFont.truetype('lcd_screen_font_1.ttf', 25)
    font_2 = ImageFont.truetype('lcd_screen_font_2.ttf', 35)
    font_3 = ImageFont.truetype('lcd_screen_font_3.ttf', 32)

    # Create blank image for drawing.
    image  = Image.new("RGB", (LCD_SCREEN_WIDTH, LCD_SCREEN_HEIGHT ), "WHITE")
    drawer = ImageDraw.Draw(image)

    # logging.info("drawer point")

    drawer.rectangle((5,10,6,11), fill = "BLACK")
    drawer.rectangle((5,25,7,27), fill = "BLACK")
    drawer.rectangle((5,40,8,43), fill = "BLACK")
    drawer.rectangle((5,55,9,59), fill = "BLACK")

    # logging.info("drawer line")
    
    drawer.line([(20, 10),(70, 60)], fill = "RED",width = 1)
    drawer.line([(70, 10),(20, 60)], fill = "RED",width = 1)
    drawer.line([(170,15),(170,55)], fill = "RED",width = 1)
    drawer.line([(150,35),(190,35)], fill = "RED",width = 1)

    # logging.info("drawer rectangle")
    
    drawer.rectangle([(20,10),(70,60)],fill = "WHITE",outline="BLUE")
    drawer.rectangle([(85,10),(130,60)],fill = "BLUE")

    # logging.info("drawer circle")
    
    drawer.arc((150,15,190,55),0, 360, fill =(0,255,0))
    drawer.ellipse((150,65,190,105), fill = (0,255,0))

    # logging.info("drawer text")
    drawer.rectangle([(0,65),(140,100)],fill = "WHITE")
    drawer.text((5, 68), 'Hello world', fill = "BLACK",font=font_1)
    drawer.rectangle([(0,115),(190,160)],fill = "RED")
    drawer.text((5, 118), 'WaveShare', fill = "WHITE",font=font_2)
    drawer.text((5, 160), '1234567890', fill = "GREEN",font=font_3)
    text= u"微雪电子"
    drawer.text((5, 200),text, fill = "BLUE",font=font_3)
    image = image.rotate(0)

    lcd_screen.display(image)
    time.sleep(5)

    # logging.info("show image")

    image = Image.open('lcd_screen_image.jpg')
    image = image.rotate(0)

    lcd_screen.display(image)
    time.sleep(5)

    lcd_screen.module_exit()

    log(INFO, '')
    log(INFO, 'Exiting...')
    log(INFO, '')
    log(INFO, '************************************')
    log(INFO, '*  Done with LCD Class testing...  *')
    log(INFO, '************************************')

    return 0


def graceful_exit(return_code):

    global lcd_screen

    if lcd_screen is not None:

        lcd_screen.module_exit()

    os._exit(return_code)

    return

log_init(DEBUG)
main()

# if __name__ == '__main__':
#
#     try:
#
#         log_init(ERROR)
#
#         main_status = main()
#
#         graceful_exit(main_status)
#
#     except KeyboardInterrupt:
#         log(ERROR, 'Keyboard interrupt...')
#         graceful_exit(1)
#
#     except Exception as error:
#         log(ERROR, 'Error: ' + str(error))
#         graceful_exit(2)
