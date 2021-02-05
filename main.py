import json
import os
import threading
import RPi.GPIO
import rotarybutton
import midireader
import xylophone
import einkscreen
import controller

from globals import *
from log     import *

setup_data = None


def print_help():

    print('')
    print('Print MIDI reader status         : m')
    print('Print MIDI file info    by index : i=2')
    print('Print MIDI file details by index : d=3')
    print('')
    print('Play a single note             : n=60')
    print('Start playing file by index    : p=2')
    print('Stop  playing file (interrupt) : s')
    print('')
    print('Set log level: l=0 > NO_LOG , 1 > ERROR,')
    print('                 2 > WARNING, 3 > INFO , 4 > DEBUG')
    print('')
    print('Press q to go for operational mode')
    print('Press x to exit with no error')
    print('Press h to display this help')
    print('')


def console_thread(midi_reader, main_controller):

    print_help()

    is_console_on = True

    while is_console_on == True:

        print('> ', end = '')

        user_input = input()

        if len(user_input) == 1:

            command = user_input[0]

            if command == 'm':
                midi_reader.print_status()
            elif command == 's':
                main_controller.stop_track()
            elif command == 'q':
                print('')
                print('***** GOING TO OPERATIONAL MODE *****')
                is_console_on = False
            elif command == 'x':
                print('***** EXITING GRACEFULLY *****')
                if control.gpio_interface == USE_RPI_GPIO:
                    RPi.GPIO.cleanup()
                os._exit(0)
            elif command == 'h':
                print_help()

        elif len(user_input) == 2:

            command = user_input[0:2]

            if command == 'sf':
                pass

        elif len(user_input) > 2 and user_input[1] == '=':

            command = user_input[0]
            value   = float(user_input[2:])

            if command == 'l':
                if value == 0:
                    log_set_level(NO_LOG )
                elif value == 1:
                    log_set_level(ERROR  )
                elif value == 2:
                    log_set_level(WARNING)
                elif value == 3:
                    log_set_level(INFO   )
                elif value == 4:
                    log_set_level(DEBUG  )
                else:
                    print('Invalid log level')
            elif command == 'i':
                midi_reader.print_file_info(int(value))
            elif command == 'd':
                midi_reader.print_file_details(int(value))
            elif command == 'n':
                main_controller.play_note(int(value))
            elif command == 'p':
                main_controller.play_track_by_index(int(value))


def main():

    global setup_data

    with open(SETUP_FILE, 'r') as json_file:
        setup_data = json.load(json_file)

    log_init(setup_data['LOG_LEVEL'])

    if setup_data['START_CONSOLE'] == 1:
        os.system('clear')
        print('')
        print('***** STARTING MY SELF PLAYING XYLOPHONE CONTROL *****')
        print('')

    if setup_data['START_CONSOLE'] == 1:
        print('********   CURRENTLY RUNNING IN CONSOLE MODE   *******')
    else:
        print('******** CURRENTLY RUNNING IN OPERATIONAL MODE *******')

    print('')

    log(INFO, 'Main >>>>>> setting up MIDI files')

    # Setup MIDI files
    midi_reader = midireader.MidiReader(setup_data['MIDI_MUSIC_DIR'])

    log(INFO, 'Main >>>>>> initiating HW parts')

    # Setup control buttons
    mode_button  = rotarybutton.RotaryStatesButton(control.gpio_interface, MODE_BUTTON_PIN_1 , MODE_BUTTON_PIN_2 , MODE_BUTTON_PIN_PRESS , [MODE.STOP, MODE.PLAY_ONE_TRACK, MODE.LOOP_ONE_TRACK, MODE.PLAY_ALL_TRACKS], True)
    track_button = rotarybutton.RotaryButton      (control.gpio_interface, TRACK_BUTTON_PIN_1, TRACK_BUTTON_PIN_2, TRACK_BUTTON_PIN_PRESS)
    tempo_button = rotarybutton.RotaryStatesButton(control.gpio_interface, TEMPO_BUTTON_PIN_1, TEMPO_BUTTON_PIN_2, TEMPO_BUTTON_PIN_PRESS, TEMPO_LIST, False)
    # io_extender_low  = ioextender.IoExtender(setup_data['I2C_BUS_NUMBER'], setup_data['MCP_23017_I2C_ADDRESS_1'])
    # io_extender_high = ioextender.IoExtender(setup_data['I2C_BUS_NUMBER'], setup_data['MCP_23017_I2C_ADDRESS_2'])

    log(INFO, 'Main >>>>>> setting xylophone')

    # Setup actual xylophone and highest level controller
    # xylophone_device = xylophone.Xylophone  (setup_data['XYLOPHONE_LOWEST_NOTE'], setup_data['XYLOPHONE_NOTES_COUNT'], io_extender_low, io_extender_high)
    xylophone_device = xylophone.Xylophone(setup_data['XYLOPHONE_LOWEST_NOTE'], setup_data['XYLOPHONE_NOTES_COUNT'], None, None)
    eink_screen      = einkscreen.EInkScreen(setup_data['I2C_BUS_NUMBER'], setup_data['E_INK_SPI_ADDRESS'], midi_reader)
    main_controller  = controller.Controller(mode_button, track_button, tempo_button, midi_reader, xylophone_device, eink_screen)

    controller_buttons_reader = threading.Thread(target = main_controller.buttons_reader_thread, name='controller_buttons_reader', args = [])
    controller_buttons_reader.start()

    controller_file_player = threading.Thread(target = main_controller.file_player_thread, name='controller_file_player', args = [])
    controller_file_player.start()

    log(INFO, 'Main >>>>>> starting console')

    if setup_data['START_CONSOLE'] == 1:
        console = threading.Thread(target = console_thread, name = 'console', args = [midi_reader, main_controller])
        console.start()

        controller_buttons_reader.join()
        controller_file_player.join   ()

    if setup_data['START_CONSOLE'] == 1:
        console.join()


if __name__ == '__main__':

    try:
        main()

    except KeyboardInterrupt:
        log(ERROR, 'Keyboard interrupt...')
        os._exit(1)

    except Exception as error:
        log(ERROR, 'Caught exception')
        log(ERROR, error             )
        os._exit(2)

    finally:
        if control.gpio_interface == USE_RPI_GPIO:
            RPi.GPIO.cleanup()
        os._exit(0)