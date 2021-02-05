import time
import midireader
import rotarybutton

from log     import *
from globals import *


class Controller:

    STATE_IDLE           = 0
    STATE_PLAYING_TRACK  = 1
    STATE_STOPPING_TRACK = 2

    def __init__(self, mode_button, track_button, tempo_button, midi_reader, xylophone, eink_screen):

        log(INFO, 'Setting up Controller')

        self.mode_button  = mode_button
        self.track_button = track_button
        self.tempo_button = tempo_button
        self.xylophone    = xylophone
        self.midi_reader  = midi_reader
        self.eink_screen  = eink_screen

        self.mode        = DEFAULT_MODE
        self.track_index = DEFAULT_TRACK
        self.track_tempo = DEFAULT_TEMPO

        self.mode_button.set_state (self.mode)
        # No need to set track button defaut state as it's not state based
        self.tempo_button.set_state(self.track_tempo)

        self.tracks_count = midi_reader.get_files_count()
        self.state        = self.STATE_IDLE

        return

    def play_note(self, note):

        self.xylophone.play_note(note)

        return

    def play_track(self):

        self.state = self.STATE_PLAYING_TRACK

        return

    def play_track_by_index(self, index):

        self.track_index = index
        self.play_track()

        return

    def stop_track(self):

        self.state = self.STATE_STOPPING_TRACK

        return

    def buttons_reader_thread(self):

        while True:

            # Deal with all 3 buttons position

            if self.mode_button.get_move() != rotarybutton.RotaryButton.DID_NOT_TURN:

                self.mode = self.mode_button.get_state()

            if self.track_button.get_move() != rotarybutton.RotaryButton.DID_NOT_TURN:

                self.track_index = self.track_button.get_value() % self.tracks_count

            if self.tempo_button.get_move() != rotarybutton.RotaryButton.DID_NOT_TURN:

                self.track_tempo = self.tempo_button.get_state()

            # Deal with all 3 buttons click status

            if self.mode_button.was_clicked() == True:

                # Possibly stop current track reading
                if self.state == self.STATE_PLAYING_TRACK:
                    self.stop_track()

                # In case of the following modes: PLAY_ONE_TRACK, LOOP_ONE_TRACK, PLAY_ALL_TRACKS
                # In case of STOP mode, there is nothing more to do : we just stop current track
                if self.mode != MODE.STOP:

                    # If we get a request to play all tracks, let's get back to the 1st track
                    if self.mode == MODE.PLAY_ALL_TRACKS:
                        self.track_index = 0

                    # Now start (or restart) selected track(s) reading
                    self.play_track()

            if self.track_button.was_clicked() == True:
                
                # Possibly stop current track reading 
                if self.state == self.STATE_PLAYING_TRACK:
                    self.stop_track()

                # Force mode change to just play that file
                self.mode = MODE.PLAY_ONE_TRACK

                # Now start (or restart) selected track reading
                self.play_track()

            if self.tempo_button.was_clicked() == True:

                pass

            # Update screen with possible new mode/track/tempo
            self.eink_screen.set_mode (self.mode       )
            self.eink_screen.set_track(self.track_index)
            self.eink_screen.set_tempo(self.track_tempo)

            time.sleep(MAIN_LOOP_SLEEP_TIME)

    def file_player_thread(self):

        while True:

            if self.state == self.STATE_IDLE:

                time.sleep(MAIN_LOOP_SLEEP_TIME)

            elif self.state == self.STATE_PLAYING_TRACK:

                start_status = self.midi_reader.start_playing_file(self.track_index)

                # If we could not start, we consider playing is done
                is_done = not start_status

                while (is_done == False) and (self.state != self.STATE_STOPPING_TRACK):

                    is_done, event = self.midi_reader.get_playing_event()

                    if is_done == False:

                        if event['type'] == midireader.MidiReader.PAUSE:
                            log(DEBUG, 'Lets pause for: {}'.format(event['value']))
                            time.sleep(event['value'])
                        else:
                            self.xylophone.play_notes(event['value'])

                if start_status == True:

                    self.midi_reader.stop_playing_file()

                if self.mode == MODE.LOOP_ONE_TRACK:

                    # Keep current track index and controller state unchanged
                    # so that we will just restart and play the same file
                    pass

                elif self.mode == MODE.PLAY_ALL_TRACKS:

                    # Increment current track index and keep controller state unchanged
                    # so that we will start and play next file; stop at the end of the list
                    if self.track_index + 1  == self.tracks_count - 1:

                        self.track_index = -1
                        self.state = self.STATE_IDLE

                    else:

                        self.track_index += 1

                else:

                    # Case of the following modes: STOP & PLAY_ONE_TRACK
                    self.track_index = -1
                    self.state    = self.STATE_IDLE

            elif self.state == self.STATE_STOPPING_TRACK:

                self.midi_reader.stop_playing_file()

                self.state = self.STATE_IDLE

            else:

                log(ERROR, 'Got to an unsupported state: {}'.format(self.state))

                self.state = self.STATE_IDLE