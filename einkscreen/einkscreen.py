from log     import *
from globals import *


class EInkScreen:

    def __init__(self, bus, address, midi_reader):

        log(INFO, 'Setting up E-ink screen')

        self.bus         = bus
        self.address     = address
        self.midi_reader = midi_reader

        self.mode        = DEFAULT_MODE
        self.track_index = DEFAULT_TRACK
        self.track_tempo = DEFAULT_TEMPO

        self.tracks_count = self.midi_reader.get_files_count()
        self.tracks       = []

        for track_index in range(0, self.tracks_count):

            name, tempo, length = self.midi_reader.get_file_info(track_index)

            track = {'name' : name, 'tempo' : tempo, 'length' : length}

            self.tracks.append(track)

        return

    def set_mode(self, mode):

        self.mode = mode

        return

    def set_track(self, index):

        self.track_index = index

        return

    def set_tempo(self, tempo):

        self.track_tempo = tempo

        return
