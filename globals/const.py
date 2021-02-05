from enum import Enum, unique

# High level constants

USE_RPI_GPIO = 0
USE_RPI_ZERO = 1
USE_PI_GPIO  = 2

SETUP_FILE     = 'setup.json'

# Mode, track select & tempo select buttons definition

MODE_BUTTON_PIN_1     = 22
MODE_BUTTON_PIN_2     = 27
MODE_BUTTON_PIN_PRESS = 17

TRACK_BUTTON_PIN_1     =  5
TRACK_BUTTON_PIN_2     =  6
TRACK_BUTTON_PIN_PRESS = 13

TEMPO_BUTTON_PIN_1     = 16
TEMPO_BUTTON_PIN_2     = 20
TEMPO_BUTTON_PIN_PRESS = 21

# E-ink screen connection definition

E_INK_SCREEN_BUSY_PIN  = 24
E_INK_SCREEN_RESET_PIN =  4
E_INK_SCREEN_DC_PIN    = 25
E_INK_SCREEN_CS_PIN    =  8
E_INK_SCREEN_SCLK_PIN  = 11
E_INK_SCREEN_SDIN_PIN  = 10

# Different available modes

@unique
class MODE(Enum):

    STOP            = 0
    PLAY_ONE_TRACK  = 1
    LOOP_ONE_TRACK  = 2
    PLAY_ALL_TRACKS = 3

# Different available tempos

TEMPO_LIST = [40,  42,  44,  46,  48,  50,  52,  54,  56,  58,  60,  63,  66,  69,  72,  76,  80,  84,  88,  92,  96,  100,  104,  108,  112,  116,  120,  126,  132,  138,  144,  152,  160,  168,  176,  184,  192,  200]

# Other, general purpose and detailed constants

MAIN_LOOP_SLEEP_TIME = 0.01

DEFAULT_MODE  = MODE.STOP
DEFAULT_TRACK = 0
DEFAULT_TEMPO = 60