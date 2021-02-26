import utils
import time
import ioextender

from log     import *
from globals import *

class Xylophone:

    def __init__(self, lowest_note, notes_count, io_extender_low, io_extender_high):

        log(INFO, 'Setup Xylophone with {} notes'.format(notes_count))

        highest_note = lowest_note + notes_count - 1

        log(DEBUG, 'Lowest  note: {} ({})'.format(utils.get_note_name_from_midi_number(lowest_note ), lowest_note ))
        log(DEBUG, 'Highest note: {} ({})'.format(utils.get_note_name_from_midi_number(highest_note), highest_note))

        self.lowest_note      = lowest_note
        self.highest_note     = highest_note
        self.io_extender_low  = io_extender_low
        self.io_extender_high = io_extender_high

        return

    def play_note(self, note):

        log(DEBUG, 'Xylophone playing note #{}'.format(note))

        if not self.lowest_note <= note <= self.highest_note:

            log(ERROR, 'Cannot play note; out of range value: {}'.format(note))
            return

        play_note = note - self.lowest_note

        if play_note < ioextender.IoExtender.IOS_COUNT:

            # self.io_extender_low.write_io(play_note, 1)
            time.sleep(control.note_length)
            # self.io_extender_low.write_io(play_note, 0)

        else:

            # self.io_extender_high.write_io(play_note, 1)
            time.sleep(control.note_length)
            # self.io_extender_high.write_io(play_note, 0)

        return

    def play_notes(self, notes):

        log(DEBUG, 'Xylophone playing note(s) #{}'.format(notes))

        for note in notes:

            if not self.lowest_note <= note <= self.highest_note:

                log(ERROR, 'Cannot play note(s); out of range value: {}'.format(note))
                return

        low_notes  = []
        high_notes = []

        for note in notes:

            play_note = note - self.lowest_note

            if play_note < ioextender.IoExtender.IOS_COUNT:
                low_notes.append(play_note)
            else:
                high_notes.append(play_note)

        if len(low_notes) != 0:

            # self.io_extender_low.write_ios(low_notes, 1)
            time.sleep(control.note_length)
            # self.io_extender_low.write_ios(low_notes, 0)

        if len(high_notes) != 0:

            # self.io_extender_high.write_ios(high_notes, 1)
            time.sleep(control.note_length)
            # self.io_extender_high.write_ios(high_notes, 0)

        return
