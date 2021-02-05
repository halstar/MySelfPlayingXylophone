import os
import utils

from mido import MidiFile, tempo2bpm
from log import *


class MidiReader:

    PAUSE = 0
    NOTES = 1

    def __init__(self, music_dir):

        log(INFO, 'Setting up MIDI reader')

        self.files            = []
        self.files_count      = 0
        self.play_in_progress = False
        self.play_file_index  = -1
        self.play_event_index = -1

        log(INFO, 'Scanning {} directory for MIDI files'.format(music_dir))

        for dirname, dirnames, filenames in os.walk(music_dir):

            for filename in filenames:

                fullname = os.path.join(dirname, filename)
                data     = MidiFile(fullname)
                tempo    = self.__get_tempo__ (data)
                events   = self.__get_events__(data)
                length   = int(data.length)

                if data.type == 2:

                    log(WARNING, 'Dropping {}, as of unsupported MIDI type 2'.format(filename))

                elif tempo == 0:

                    log(WARNING, 'Dropping {}, as no tempo was found'.format(filename))

                elif len(events) == 0:

                    log(WARNING, 'Dropping {}, as no events were found'.format(filename))

                else:

                    file_data = {}

                    file_data['name'       ] = filename
                    file_data['tempo'      ] = tempo
                    file_data['length'     ] = length
                    file_data['events'      ] = events
                    file_data['notes_count'] = len(events)

                    self.files.append(file_data)
                    self.files_count += 1

                    log(DEBUG, 'Registered file #{}: {}'.format(self.files_count, filename))

        log(INFO, 'Found & parsed {} MIDI files'.format(self.files_count))

        return

    @staticmethod
    def __get_tempo__(file_data):

        for track_index, track_data in enumerate(file_data.tracks):

            for msg in track_data:

                if msg.is_meta == True and msg.type == 'set_tempo':

                    return int(tempo2bpm(msg.tempo))

        return 0

    @staticmethod
    def __get_events__(file_data):

        events = []

        for msg in file_data:

            if msg.is_meta == True:

                # Nothing to do
                pass

            elif msg.type == 'note_on' or msg.type == 'note_off':

                if msg.velocity != 0 and msg.time == 0:

                    if len(events) != 0 and events[-1]['type'] == MidiReader.NOTES:
                        events[-1]['value'].append(msg.note)
                    else:
                        events.append({'type'  : MidiReader.NOTES,
                                       'value' : [msg.note]})

                elif msg.velocity != 0 and msg.time != 0:

                    if len(events) != 0 and events[-1]['type'] == MidiReader.PAUSE:
                        events[-1]['value'] += msg.time
                    else:
                        events.append({'type' : MidiReader.PAUSE,
                                       'value': msg.time})

                    events.append({'type' : MidiReader.NOTES,
                                   'value': [msg.note]})

                elif msg.velocity == 0 and msg.time != 0:

                    if len(events) != 0 and events[-1]['type'] == MidiReader.PAUSE:
                        events[-1]['value'] += msg.time
                    else:
                        events.append({'type' : MidiReader.PAUSE,
                                       'value': msg.time})

                elif msg.velocity == 0 and msg.time == 0:

                    # Nothing to do
                    pass

            elif msg.time != 0:

                if len(events) != 0 and events[-1]['type'] == MidiReader.PAUSE:
                    events[-1]['value'] += msg.time
                else:
                    events.append({'type' : MidiReader.PAUSE,
                                   'value': msg.time})

            else:

                # Nothing to do
                pass

        return events

    def get_files_count(self):

        return self.files_count

    def get_file_info(self, index):

        if not 0 <= index < self.files_count:

            log(ERROR, 'Cannot get MIDI file info; out of range index: {}'.format(index))
            return None

        else:

            return self.files[index]['name'], self.files[index]['tempo'], self.files[index]['length']

    def start_playing_file(self, index):

        return_status = False

        if not 0 <= index < self.files_count:

            log(ERROR, 'Cannot start playing file; out of range index: {}'.format(index))

        elif self.play_in_progress == True:

            log(ERROR, 'Cannot start playing file; playing already in progress')

        else:

            file_data = self.files[index]

            log(INFO, 'Starting playing file #{}: {}'.format(index, file_data['name']))

            self.play_in_progress = True
            self.play_file_index  = index
            self.play_event_index  = 0
            return_status         = True

        return return_status

    def get_playing_event(self):

        return_status = True
        return_event  = None

        if self.play_in_progress == False or self.play_file_index == -1 or self.play_event_index == -1:

            log(ERROR, 'Cannot step playing; no playing started')

        else:

            file_data = self.files[self.play_file_index]

            if self.play_event_index < file_data['notes_count']:

                log(DEBUG, 'Do step #{} on file #{}'.format(self.play_event_index, self.play_file_index))

                return_event           = file_data['events'][self.play_event_index]
                self.play_event_index += 1
                return_status          = False

            else:

                log(DEBUG, 'End of file #{} reached'.format(self.play_file_index))
                return_status = True

        return return_status, return_event

    def stop_playing_file(self):

        return_status = False

        if self.play_in_progress == False or self.play_file_index == -1 or self.play_event_index == -1:

            log(ERROR, 'Cannot stop playing; no playing started')

        else:

            file_data = self.files[self.play_file_index]

            log(INFO, 'Stopping playing file #{}: {}'.format(self.play_file_index, file_data['name']))

            self.play_in_progress = False
            self.play_file_index  = -1
            self.play_event_index  = -1
            return_status         = True

        return return_status

    def print_status(self):

        print('Total files count: {}'.format(self.files_count     ))
        print('Play file index  : {}'.format(self.play_file_index ))
        print('Play event index : {}'.format(self.play_event_index))

        if self.play_in_progress == True:
            print('Play in progress ')
        else:
            print('Play not in progress ')
        return

    def print_file_info(self, index):

        if not 0 <= index < self.files_count:

            log(ERROR, 'Cannot read MIDI file; out of range index: {}'.format(index))

        else:

            file_data = self.files[index]

            print('File #{}: {}'.format(index, file_data['name']))

            seconds = int(file_data['length'] % 60)
            minutes = int(file_data['length'] / 60)

            print('\tTempo  : {}'.format   (file_data['tempo']      ))
            print('\tLength : {}:{}'.format(minutes, seconds        ))
            print('\tNotes #: {}'.format   (file_data['notes_count']))

        return

    def print_file_details(self, index):

        if not 0 <= index < self.files_count:

            log(ERROR, 'Cannot read MIDI file; out of range index: {}'.format(index))

        else:

            file_data = self.files[index]

            print('File #{}: {}'.format(index, file_data['name']))

            for event in file_data['events']:

                if event['type'] ==  self.PAUSE:

                    print('\tPause: {}'.format(event['value']))

                # Event is a single note, or several notes
                else:

                    print('\tNotes: ', end='', flush=True)

                    for note in event['value']:
                        print('{} '.format(utils.get_note_name_from_midi_number(note)), end='', flush=True)

                    print('')

        return
