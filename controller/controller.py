import time

from log     import *
from globals import *
from utils   import *


class Controller:

    STATE_IDLE           = 0
    STATE_PLAYING_TRACK  = 1
    STATE_STOPPING_TRACK = 2

    WELCOME_SOUND = [
        {'type': IS_NOTES, 'value': [53]},
        {'type': IS_PAUSE, 'value': 0.3 },
        {'type': IS_NOTES, 'value': [54]},
        {'type': IS_PAUSE, 'value': 0.3 },
        {'type': IS_NOTES, 'value': [55]},
        {'type': IS_PAUSE, 'value': 0.3 }
    ]

    WELCOME_SOUND_TEMPO = 60

    def __init__(self, mode_button, track_button, tempo_button, midi_reader, xylophone, display):

        log(INFO, 'Setting up Controller')

        self.mode_button      = mode_button
        self.track_button     = track_button
        self.tempo_button     = tempo_button
        self.xylophone        = xylophone
        self.midi_reader      = midi_reader
        self.display          = display
        self.auto_mode_change = False

        self.mode        = DEFAULT_MODE
        self.track_index = DEFAULT_TRACK
        self.__set_track_tempo__(self.midi_reader.get_file_tempo(self.track_index))
        self.__set_play_tempo__ (self.track_tempo)
        self.__set_tempo_ratio__()

        self.mode_button.set_state (self.mode       )
        self.track_button.set_state(self.track_index)
        self.tempo_button.set_state(self.track_tempo)

        self.tracks_count = midi_reader.get_files_count()
        self.state        = self.STATE_IDLE

        return

    def __set_track_tempo__(self, tempo):

        self.track_tempo = tempo

        return

    def __set_play_tempo__(self, tempo):

        self.play_tempo = tempo

        return

    def __set_tempo_ratio__(self):

        self.tempo_ratio = self.track_tempo / self.play_tempo

        return

    def __play_event__(self, event):

        if event['type'] == IS_PAUSE:

            pause_duration = event['value'] * self.tempo_ratio

            self.xylophone.pause(pause_duration)

        else:

            self.xylophone.play_notes(event['value'])

        return

    def play_welcome_sound(self):

        log(INFO, 'Playing welcome sound')

        # Save tempo of the currently selected track
        saved_tempo = self.track_tempo

        self.__set_track_tempo__(self.WELCOME_SOUND_TEMPO)
        self.__set_play_tempo__ (self.WELCOME_SOUND_TEMPO)
        self.__set_tempo_ratio__()

        for event in self.WELCOME_SOUND:

            self.__play_event__(event)

        # Restore saved tempo
        self.__set_track_tempo__(saved_tempo)
        self.__set_play_tempo__ (saved_tempo)
        self.__set_tempo_ratio__()

        return

    def play_note_from_console(self, note):

        self.xylophone.play_note(note)

        return

    def play_notes_from_console(self, notes):

        self.xylophone.play_notes(notes)

        return

    def play_track(self):

        self.state = self.STATE_PLAYING_TRACK

        return

    def play_track_from_console(self, index, use_file_tempo):

        # Force track change to show up on display
        self.track_button.set_state(index)

        self.__set_track_tempo__(self.midi_reader.get_file_tempo(index))
        if use_file_tempo == True:
            self.__set_play_tempo__(self.track_tempo)
        else:
            # Do not change play tempo; use last specific value set on console
            pass
        self.__set_tempo_ratio__()

        # Force mode change to just play that file
        self.mode = MODE.PLAY_ONE_TRACK
        self.mode_button.set_state(self.mode)

        # Sleep a bit to make sure that buttons reader thread had time to update
        time.sleep(MAIN_LOOP_SLEEP_TIME)

        self.play_track()

        return

    def stop_track(self):

        self.state = self.STATE_STOPPING_TRACK

        return

    def set_tempo_from_console(self, tempo):

        # Force tempo change to show up on display
        self.__set_play_tempo__    (tempo)
        self.__set_tempo_ratio__   ()
        self.tempo_button.set_state(tempo)

        # Sleep a bit to make sure that buttons reader thread had time to update
        time.sleep(MAIN_LOOP_SLEEP_TIME)

        return

    def buttons_reader_thread(self):

        log(INFO, 'Starting Controller\'s buttons reader thread')

        while True:

            # Deal with all 3 buttons position
            self.mode        = self.mode_button.get_state ()
            self.track_index = self.track_button.get_state()
            preset_tempo     = self.tempo_button.get_state()

            # Possibly update screen with possible new preset mode/track/tempo
            self.display.preset_mode      (self.mode       )
            self.display.preset_play_tempo(preset_tempo    )
            self.display.set_track_tempo  (self.track_index)
            self.display.set_track_length (self.track_index)
            self.display.preset_track     (self.track_index)

            # Deal with all 3 buttons click status

            if (self.mode_button.was_clicked() == True) or (self.auto_mode_change == True):

                self.auto_mode_change = False

                self.display.set_mode(self.mode)

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
                self.mode_button.set_state(self.mode)
                self.display.set_mode     (self.mode)

                # Force tempo change to play that file at its default pace
                self.__set_track_tempo__    (self.midi_reader.get_file_tempo(self.track_index))
                self.__set_play_tempo__     (self.track_tempo)
                self.__set_tempo_ratio__    (                )
                self.tempo_button.set_state (self.track_tempo)
                self.display.set_play_tempo (self.track_tempo)

                # Update the requested track on display
                self.display.set_track(self.track_index)

                # Now start (or restart) selected track reading
                self.play_track()

            if self.tempo_button.was_clicked() == True:

                self.__set_play_tempo__    (preset_tempo)
                self.__set_tempo_ratio__   (            )
                self.display.set_play_tempo(preset_tempo)

            # Now actually refresh display with all possible previous updates
            self.display.refresh()

            time.sleep(MAIN_LOOP_SLEEP_TIME)

    def file_player_thread(self):

        while True:

            if self.state == self.STATE_IDLE:

                time.sleep(MAIN_LOOP_SLEEP_TIME)

            elif self.state == self.STATE_PLAYING_TRACK:

                start_status = self.midi_reader.start_playing_file(self.track_index)

                # If we could not start, we consider playing is done
                is_done = not start_status

                # File reading can be interrupted by pushing MODE button to STOP
                while (is_done == False) and (self.state != self.STATE_STOPPING_TRACK):

                    is_done, event = self.midi_reader.get_playing_event()

                    if is_done == False:

                        self.__play_event__(event)

                # Stop file reading only if we actually started reading one
                if start_status == True:

                    self.midi_reader.stop_playing_file()

                if self.mode == MODE.LOOP_ONE_TRACK:

                    # Keep current track index and controller state unchanged
                    # so that we will just restart and play the same file.
                    # Just sleep a bit in between track repetitions...
                    time.sleep(INTER_TRACKS_SLEEP)

                elif self.mode == MODE.PLAY_ALL_TRACKS:

                    # Increment current track index and keep controller state unchanged
                    # so that we will start and play next file; stop at the end of the list
                    if self.track_index + 1  == self.tracks_count:

                        self.state = self.STATE_STOPPING_TRACK

                    else:

                        self.track_index += 1

                        # Force track change to show up
                        self.track_button.set_state(self.track_index)

                        # Sleep a bit in between tracks...
                        time.sleep(INTER_TRACKS_SLEEP)

                else:

                    # Case of the following modes: STOP & PLAY_ONE_TRACK
                    self.state = self.STATE_STOPPING_TRACK

            elif self.state == self.STATE_STOPPING_TRACK:

                # Force mode change to show up that we are now stopped
                self.mode = MODE.STOP
                self.mode_button.set_state(self.mode)
                self.auto_mode_change = True

                self.state = self.STATE_IDLE

            else:

                log(ERROR, 'Got to an unsupported state: {}'.format(self.state))

                self.state = self.STATE_IDLE

    def print_status(self):

        print('Tracks count: {}'.format(self.tracks_count))
        print('Track index : {}'.format(self.track_index ))
        print('Track tempo : {}'.format(self.track_tempo ))
        print('Play  tempo : {}'.format(self.play_tempo  ))
        print('Tempo ratio : {}'.format(self.tempo_ratio ))

        return