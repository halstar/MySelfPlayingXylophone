from enum import Enum, unique

# High level constants

USE_RPI_GPIO = 0
USE_RPI_ZERO = 1
USE_PI_GPIO  = 2

SETUP_FILE     = 'setup.json'

# Mode, track select & tempo select buttons definition

# MODE_BUTTON_PIN_1     = 22
# MODE_BUTTON_PIN_2     = 27
# MODE_BUTTON_PIN_PRESS = 18

MODE_BUTTON_PIN_1     = 5
MODE_BUTTON_PIN_2     = 6
MODE_BUTTON_PIN_PRESS = 13

# TRACK_BUTTON_PIN_1     =  5
# TRACK_BUTTON_PIN_2     =  6
# TRACK_BUTTON_PIN_PRESS = 13

TRACK_BUTTON_PIN_1     = 16
TRACK_BUTTON_PIN_2     = 20
TRACK_BUTTON_PIN_PRESS = 21

# TEMPO_BUTTON_PIN_1     = 16
# TEMPO_BUTTON_PIN_2     = 20
# TEMPO_BUTTON_PIN_PRESS = 21

TEMPO_BUTTON_PIN_1     = 22
TEMPO_BUTTON_PIN_2     = 27
TEMPO_BUTTON_PIN_PRESS = 18

# E-ink screen connection definition

E_INK_SCREEN_BUSY_PIN  = 24
E_INK_SCREEN_RESET_PIN = 17
E_INK_SCREEN_DC_PIN    = 25
E_INK_SCREEN_CS_PIN    =  8
E_INK_SCREEN_SCLK_PIN  = 11
E_INK_SCREEN_SDIN_PIN  = 10

# Different available modes

@unique
class MODE(Enum):

    PLAY_ONE_TRACK  = 0
    PLAY_ALL_TRACKS = 1
    LOOP_ONE_TRACK  = 2
    STOP            = 3

# Other, general purpose and detailed constants

MAIN_LOOP_SLEEP_TIME = 0.01

E_INK_SCREEN_WIDTH  = 128
E_INK_SCREEN_HEIGHT = 296

DEFAULT_MODE        = MODE.STOP
DEFAULT_TRACK       = 0
DEFAULT_NOTE_LENGTH = 0.015
INTER_TRACKS_SLEEP  = 3