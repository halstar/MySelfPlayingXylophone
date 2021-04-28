from enum import Enum, unique

# High level constants

USE_RPI_GPIO = 0
USE_RPI_ZERO = 1
USE_PI_GPIO  = 2

SETUP_FILE     = 'setup.json'

# Mode, track select & tempo select buttons definition

MODE_BUTTON_PIN_PRESS = 17
MODE_BUTTON_PIN_1     = 27
MODE_BUTTON_PIN_2     = 22

TRACK_BUTTON_PIN_PRESS = 14
TRACK_BUTTON_PIN_1     = 15
TRACK_BUTTON_PIN_2     = 18

TEMPO_BUTTON_PIN_PRESS = 16
TEMPO_BUTTON_PIN_1     = 20
TEMPO_BUTTON_PIN_2     = 21

# LCD screen connection definition

LCD_SCREEN_BL_PIN    =  5
LCD_SCREEN_RESET_PIN =  6
LCD_SCREEN_DC_PIN    = 13
LCD_SCREEN_CS_PIN    =  8
LCD_SCREEN_SDIN_PIN  = 10
LCD_SCREEN_SCLK_PIN  = 11

# Note: I2C reserved pins are #2 for SDA & #3 for SCL

# Different available modes

@unique
class MODE(Enum):

    PLAY_ONE_TRACK  = 0
    PLAY_ALL_TRACKS = 1
    LOOP_ONE_TRACK  = 2
    STOP            = 3

# Other, general purpose and detailed constants

BUTTONS_READER_THREAD_SLEEP_TIME = 0.005
FILE_PLAYER_THREAD_SLEEP_TIME    = 0.100

LCD_SCREEN_WIDTH  = 240
LCD_SCREEN_HEIGHT = 320

DEFAULT_MODE        = MODE.STOP
DEFAULT_TRACK       = 0
DEFAULT_NOTE_LENGTH = 0.020
INTER_TRACKS_SLEEP  = 5