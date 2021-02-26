import os

from log     import *
from globals import *

from PIL import Image, ImageDraw, ImageFont


class Display:

    BIGGER_LINE_HEIGHT   =  30
    HORIZONTAL_MARGIN    =  10
    LEFT_PANEL_MID_WIDTH = 100
    LEFT_PANEL_WIDTH     = 160
    TITLE_FONT_HEIGHT    =  18
    TEXT_FONT_HEIGHT     =  16
    SELECTION_MARGIN     =   5

    SMALLER_LINE_HEIGHT  = 20
    DISPLAY_TRACKS_COUNT =  4

    SETTINGS_TITLE  = 'Main settings'
    TRACKS_TITLE    = 'Track selection'

    PLAY_TRACK_TEXT = 'Play track'
    PLAY_ALL_TEXT   = 'Play all'
    LOOP_TRACK_TEXT = 'Loop track'
    STOP_TEXT       = 'Stop'
    TEMPO_TEXT      = 'Tempo: '

    def __init__(self, e_ink_screen, midi_reader):

        log(INFO, 'Setting up Display class')

        self.e_ink_screen = e_ink_screen
        self.midi_reader  = midi_reader

        self.mode               = None
        self.mode_preset        = None
        self.track_index        = None
        self.track_preset_index = None
        self.tempo              = None
        self.tempo_preset       = None
        self.tracks_count       = self.midi_reader.get_files_count()
        self.tracks             = []

        self.title_vertical_offset = (self.BIGGER_LINE_HEIGHT - self.TITLE_FONT_HEIGHT) / 2
        self.text_vertical_offset  = (self.BIGGER_LINE_HEIGHT - self.TEXT_FONT_HEIGHT ) / 2

        for track_index in range(0, self.tracks_count):

            name, tempo, length = self.midi_reader.get_file_info(track_index)

            name_without_ext, ext = os.path.splitext(name)

            if len(name_without_ext) > 13:

                name_without_ext = name_without_ext[:13] + '...'

            track = {'name' : name_without_ext, 'tempo' : tempo, 'length' : length}

            self.tracks.append(track)

        self.title_font = ImageFont.truetype('display/display_font.ttc', self.TITLE_FONT_HEIGHT)
        self.text_font  = ImageFont.truetype('display/display_font.ttc', self.TEXT_FONT_HEIGHT )

        self.image  = Image.new('1', (E_INK_SCREEN_HEIGHT, E_INK_SCREEN_WIDTH), 255)
        self.drawer = ImageDraw.Draw(self.image)

        self.play_track_text_width, height = self.drawer.textsize(self.PLAY_TRACK_TEXT, font = self.text_font)
        self.play_all_text_width  , height = self.drawer.textsize(self.PLAY_ALL_TEXT  , font = self.text_font)
        self.loop_track_text_width, height = self.drawer.textsize(self.LOOP_TRACK_TEXT, font = self.text_font)
        self.stop_text_width      , height = self.drawer.textsize(self.STOP_TEXT      , font = self.text_font)
        self.tempo_text_width     , height = self.drawer.textsize(self.TEMPO_TEXT     , font = self.text_font)
        self.tempo_value_width    , height = self.drawer.textsize('123'               , font = self.text_font)

        self.e_ink_screen.module_init()

        self.drawer.rectangle((0, 0, E_INK_SCREEN_HEIGHT - 1, E_INK_SCREEN_WIDTH - 1), outline = 0)

        # Draw Main settings title
        self.drawer.text((self.HORIZONTAL_MARGIN,
                          self.title_vertical_offset),
                          self.SETTINGS_TITLE,
                          font = self.title_font,
                          fill = 0)
        self.drawer.line((0,
                          self.BIGGER_LINE_HEIGHT,
                          E_INK_SCREEN_HEIGHT - 1,
                          self.BIGGER_LINE_HEIGHT),
                          fill = 0)

        # Initialize Mode drawing
        self.__draw_mode_text__(MODE.PLAY_ONE_TRACK , False)
        self.__draw_mode_text__(MODE.PLAY_ALL_TRACKS, False)
        self.__draw_mode_text__(MODE.LOOP_ONE_TRACK , False)
        self.__draw_mode_text__(MODE.STOP           , False)

        self.drawer.line((0,
                          self.BIGGER_LINE_HEIGHT * 3,
                          self.LEFT_PANEL_WIDTH,
                          self.BIGGER_LINE_HEIGHT * 3),
                          fill = 0)

        # Initialize Tempo drawing
        self.drawer.text((self.HORIZONTAL_MARGIN,
                          self.BIGGER_LINE_HEIGHT * 3 + self.text_vertical_offset),
                          self.TEMPO_TEXT,
                          font = self.text_font,
                          fill = 0)

        self.drawer.line((self.LEFT_PANEL_WIDTH,
                          0,
                          self.LEFT_PANEL_WIDTH,
                          E_INK_SCREEN_WIDTH - 1),
                          fill = 0)

        # Draw Track selection title
        self.drawer.text((self.LEFT_PANEL_WIDTH + self.HORIZONTAL_MARGIN,
                          self.title_vertical_offset),
                          self.TRACKS_TITLE,
                          font = self.title_font,
                          fill = 0)

        # Initialize Tracks drawing

        for line_index in range(0, self.DISPLAY_TRACKS_COUNT):

            self.__draw_track_text__(line_index, line_index, False)

        e_ink_screen.display_base(self.image)

        self.set_mode (DEFAULT_MODE )
        self.set_track(DEFAULT_TRACK)
        self.set_tempo(DEFAULT_TEMPO)

        return

    def __draw_mode_text__(self, mode, is_inverted):

        if is_inverted == True:
            fill_color = 255
        else:
            fill_color = 0

        if mode == MODE.PLAY_ONE_TRACK:

            self.drawer.text((self.HORIZONTAL_MARGIN,
                              self.BIGGER_LINE_HEIGHT * 1 + self.text_vertical_offset),
                              self.PLAY_TRACK_TEXT,
                              font = self.text_font,
                              fill = fill_color)

        elif mode == MODE.PLAY_ALL_TRACKS:

            self.drawer.text((self.LEFT_PANEL_MID_WIDTH,
                              self.BIGGER_LINE_HEIGHT * 1 + self.text_vertical_offset),
                              self.PLAY_ALL_TEXT,
                              font = self.text_font,
                              fill = fill_color)

        elif mode == MODE.LOOP_ONE_TRACK:

            self.drawer.text((self.HORIZONTAL_MARGIN,
                              self.BIGGER_LINE_HEIGHT * 2 + self.text_vertical_offset),
                              self.LOOP_TRACK_TEXT,
                              font = self.text_font,
                              fill = fill_color)

        elif mode == MODE.STOP:

            self.drawer.text((self.LEFT_PANEL_MID_WIDTH,
                              self.BIGGER_LINE_HEIGHT * 2 + self.text_vertical_offset),
                              self.STOP_TEXT,
                              font = self.text_font,
                              fill = fill_color)

        return

    def __draw_tempo_value__(self, tempo_value):

        self.drawer.text((self.HORIZONTAL_MARGIN + self.tempo_text_width + self.HORIZONTAL_MARGIN,
                          self.BIGGER_LINE_HEIGHT * 3 + self.text_vertical_offset),
                          str(tempo_value),
                          font = self.text_font,
                          fill = 0)

        return

    def __draw_track_text__(self, track_index, line_index, is_inverted):

        if is_inverted == True:
            fill_color = 255
        else:
            fill_color = 0

        log(INFO, 'track {} / {}'.format(track_index, self.tracks[track_index]['name']))

        self.drawer.text((self.LEFT_PANEL_WIDTH + self.HORIZONTAL_MARGIN,
                          self.BIGGER_LINE_HEIGHT + self.SMALLER_LINE_HEIGHT * line_index + self.text_vertical_offset),
                          self.tracks[track_index]['name'],
                          font = self.text_font,
                          fill = fill_color)

        return

    def __unset_mode__(self, mode):

        if mode == MODE.PLAY_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 1 + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN + self.play_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 - self.SELECTION_MARGIN),
                                   fill = 255)

            self.__draw_mode_text__(MODE.PLAY_ONE_TRACK, False)


        elif mode == MODE.PLAY_ALL_TRACKS:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 1 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH + self.play_all_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 - self.SELECTION_MARGIN),
                                   fill = 255)

            self.__draw_mode_text__(MODE.PLAY_ALL_TRACKS, False)

        elif mode == MODE.LOOP_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN + self.loop_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 3 - self.SELECTION_MARGIN),
                                   fill = 255)

            self.__draw_mode_text__(MODE.LOOP_ONE_TRACK, False)

        elif mode == MODE.STOP:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH + self.stop_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 3 - self.SELECTION_MARGIN),
                                   fill = 255)

            self.__draw_mode_text__(MODE.STOP, False)

        return

    def preset_mode(self, mode):

        if mode == self.mode_preset:
            return

        log(INFO, 'Display preset mode: {}'.format(mode.name))

        if self.mode_preset != self.mode:
            self.__unset_mode__(self.mode_preset)

        if mode == MODE.PLAY_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 1 + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN + self.play_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 - self.SELECTION_MARGIN),
                                   outline = 0)

        elif mode == MODE.PLAY_ALL_TRACKS:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 1 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH + self.play_all_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 - self.SELECTION_MARGIN),
                                   outline = 0)

        elif mode == MODE.LOOP_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN + self.loop_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 3 - self.SELECTION_MARGIN),
                                   outline = 0)

        elif mode == MODE.STOP:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH + self.stop_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 3 - self.SELECTION_MARGIN),
                                   outline = 0)


        else:

            log(ERROR, 'Got an unsupported mode to preset: {}'.format(mode.name))

        self.e_ink_screen.display_partial(self.image)

        self.mode_preset = mode

        return

    def set_mode(self, mode):

        if mode == self.mode:
            return

        log(INFO, 'Display set mode: {}'.format(mode.name))

        self.__unset_mode__(self.mode)

        if mode == MODE.PLAY_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN + self.play_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 - self.SELECTION_MARGIN),
                                   fill = 0)

            self.__draw_mode_text__(MODE.PLAY_ONE_TRACK, True)

        elif mode == MODE.PLAY_ALL_TRACKS:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 1 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH + self.play_all_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 - self.SELECTION_MARGIN),
                                   fill = 0)

            self.__draw_mode_text__(MODE.PLAY_ALL_TRACKS, True)

        elif mode == MODE.LOOP_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN + self.loop_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 3 - self.SELECTION_MARGIN),
                                   fill = 0)

            self.__draw_mode_text__(MODE.LOOP_ONE_TRACK, True)

        elif mode == MODE.STOP:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH + self.stop_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 3 - self.SELECTION_MARGIN),
                                   fill = 0)

            self.__draw_mode_text__(MODE.STOP, True)

        else:

            log(ERROR, 'Got an unsupported mode to set: {}'.format(mode.name))

        self.e_ink_screen.display_partial(self.image)

        self.mode_preset = mode
        self.mode        = mode

        return

    def preset_track(self, index):

        if index == self.track_preset_index:
            return

        log(INFO, 'Display preset track: {}'.format(index))

        self.e_ink_screen.display_partial(self.image)

        self.track_preset_index = index

        return

    def set_track(self, index):

        if index == self.track_index:
            return

        log(INFO, 'Display set track: {}'.format(index))

        self.e_ink_screen.display_partial(self.image)

        self.track_index = index

        return

    def __unset_tempo__(self):

        self.drawer.rectangle((self.HORIZONTAL_MARGIN + self.tempo_text_width - self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 3 + self.SELECTION_MARGIN,
                               self.HORIZONTAL_MARGIN + self.tempo_text_width + self.tempo_value_width + self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 4 - self.SELECTION_MARGIN),
                               fill = 255)

        return

    def preset_tempo(self, tempo):

        if tempo == self.tempo_preset:
            return

        log(INFO, 'Display preset tempo: {}'.format(tempo))

        self.__unset_tempo__()

        self.drawer.rectangle((self.HORIZONTAL_MARGIN + self.tempo_text_width + self.HORIZONTAL_MARGIN - self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 3 + self.SELECTION_MARGIN,
                               self.HORIZONTAL_MARGIN + self.tempo_text_width + self.tempo_value_width + self.HORIZONTAL_MARGIN + self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 4 - self.SELECTION_MARGIN),
                               outline = 0)

        self.__draw_tempo_value__(tempo)

        self.e_ink_screen.display_partial(self.image)

        self.tempo_preset = tempo

        return

    def set_tempo(self, tempo):

        if tempo == self.tempo:
            return

        log(INFO, 'Display set tempo: {}'.format(tempo))

        self.drawer.rectangle((self.HORIZONTAL_MARGIN + self.tempo_text_width + self.HORIZONTAL_MARGIN - self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 3 + self.SELECTION_MARGIN,
                               self.HORIZONTAL_MARGIN + self.tempo_text_width + self.tempo_value_width + self.HORIZONTAL_MARGIN + self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 4 - self.SELECTION_MARGIN),
                               fill = 255)

        self.__draw_tempo_value__(tempo)

        self.e_ink_screen.display_partial(self.image)

        self.tempo_preset = tempo
        self.tempo        = tempo

        return
