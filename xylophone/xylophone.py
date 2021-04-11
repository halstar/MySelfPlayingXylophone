import time
import ioextender

from log     import *
from utils   import *
from globals import *


class Xylophone:

    def __init__(self, lowest_note, notes_count, max_simultaneous_notes, io_extender_low, io_extender_high):

        log(INFO, 'Setup Xylophone with {} notes'.format(notes_count))

        highest_note = lowest_note + notes_count - 1

        log(DEBUG, 'Lowest  note: {} ({})'.format(get_note_name_from_midi_number(lowest_note ), lowest_note ))
        log(DEBUG, 'Highest note: {} ({})'.format(get_note_name_from_midi_number(highest_note), highest_note))

        self.lowest_note            = lowest_note
        self.highest_note           = highest_note
        self.max_simultaneous_notes = max_simultaneous_notes
        self.io_extender_low        = io_extender_low
        self.io_extender_high       = io_extender_high

        return

    def play_note(self, note):

        log(DEBUG, 'Xylophone playing note #{}'.format(note))

        if not self.lowest_note <= note <= self.highest_note:

            log(ERROR, 'Cannot play note; out of range value: {}'.format(note))
            return

        note_pin = note - self.lowest_note

        if note_pin < ioextender.IoExtender.IOS_COUNT:

            self.io_extender_low.write_io(note_pin, 1)
            time.sleep(control.note_length)
            self.io_extender_low.write_io(note_pin, 0)

        else:

            self.io_extender_high.write_io(note_pin - ioextender.IoExtender.IOS_COUNT, 1)
            time.sleep(control.note_length)
            self.io_extender_high.write_io(note_pin - ioextender.IoExtender.IOS_COUNT, 0)

        return

    def play_notes(self, notes):

        log(DEBUG, 'Xylophone playing note(s) {}'.format(notes))

        if len(notes) > self.max_simultaneous_notes:

            log(WARNING, 'Maximum allowed simultaneous notes passed; dropping notes: {}'.format(notes[self.max_simultaneous_notes:]))

            # Drop the last notes in the list, that is the highest ones,
            # the ones with the least expressive sound on a xylophone.
            notes = notes[:self.max_simultaneous_notes]

        for note in notes:

            if not self.lowest_note <= note <= self.highest_note:

                log(ERROR, 'Cannot play note(s); out of range value: {}'.format(note))
                return

        low_notes_0  = []
        low_notes_1  = []
        high_notes_0 = []
        high_notes_1 = []

        for note in notes:

            note_pin = note - self.lowest_note

            pin_value_0 = {}
            pin_value_1 = {}

            pin_value_0['value'] = 0
            pin_value_1['value'] = 1

            if note_pin < ioextender.IoExtender.IOS_COUNT:

                pin_value_0['pin'] = note_pin
                pin_value_1['pin'] = note_pin

                low_notes_0.append(pin_value_0)
                low_notes_1.append(pin_value_1)

            else:

                pin_value_0['pin'] = note_pin - ioextender.IoExtender.IOS_COUNT
                pin_value_1['pin'] = note_pin - ioextender.IoExtender.IOS_COUNT

                high_notes_0.append(pin_value_0)
                high_notes_1.append(pin_value_1)

        if len(low_notes_1) != 0:

            self.io_extender_low.write_ios(low_notes_1)

        if len(high_notes_1) != 0:

            self.io_extender_high.write_ios(high_notes_1)

        time.sleep(control.note_length)

        if len(low_notes_0) != 0:

            self.io_extender_low.write_ios(low_notes_0)

        if len(high_notes_0) != 0:

            self.io_extender_high.write_ios(high_notes_0)

        return

    @staticmethod
    def pause(pause_duration):

        log(DEBUG, 'Xylophone pausing for: {} s'.format(pause_duration))

        # Input file format, out of our tool midif_files_filter.py, is such as notes event
        # and pause events are systematically stored one after another (we never get notes
        # after notes of pause after pause). As notes events executes with a fixed duration,
        # we have to remove that duration, - as that already elapsed, - to the upcoming pause.
        actual_pause_duration = pause_duration - control.note_length

        # This should not occur that much, - as note length is very short, - but just in case
        # pause duration gets negative, it's not time to sleep: let's go straight to next notes!
        if actual_pause_duration <= 0:
            log(WARNING, 'Got a very short pause ({}): bypassing sleep'.format(pause_duration))
        else:
            time.sleep(actual_pause_duration)

        return
