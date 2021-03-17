import os
import math

from log     import *
from utils   import *
from globals import *

from PIL import Image, ImageDraw, ImageFont


class Display:

    BIGGER_LINE_HEIGHT   =  35
    HORIZONTAL_MARGIN    =  10
    LEFT_PANEL_MID_WIDTH = 100
    LEFT_PANEL_3_4_WIDTH = 113
    LEFT_PANEL_WIDTH     = 160
    TITLE_FONT_HEIGHT    =  18
    TEXT_FONT_HEIGHT     =  16

    SMALLER_LINE_HEIGHT  = 21
    DISPLAY_TRACKS_COUNT =  9
    TRIANGLES_AREA_WIDTH = 25
    SELECTION_MARGIN     =  5

    INIT_IMAGE = 'display/xylo.png'

    SETTINGS_TITLE = 'Main settings'
    TRACKS_TITLE   = 'Track selection'

    PLAY_TRACK_TEXT   = 'Play track'
    PLAY_ALL_TEXT     = 'Play all'
    LOOP_TRACK_TEXT   = 'Loop track'
    STOP_TEXT         = 'Stop'
    PLAY_TEMPO_TEXT   = 'Play  tempo:'
    TRACK_TEMPO_TEXT  = 'Track tempo:'
    TRACK_LENGTH_TEXT = 'Track length:'

    BACKGROUND_COLOR    = 'WHITE'
    LINES_COLOR         = 'BLACK'
    DEFAULT_TEXT_COLOR  = 'BLACK'
    INVERTED_TEXT_COLOR = 'WHITE'
    PRESET_COLOR        = 'BLACK'
    SET_COLOR           = 'BLACK'
    TRIANGLES_COLOR     = 'BLACK'

    def __init__(self, lcd_screen):

        log(INFO, 'Setting up Display class')

        self.lcd_screen  = lcd_screen
        self.midi_reader = None

        self.mode               = None
        self.mode_preset        = None
        self.track_index        = 0
        self.track_preset_index = None
        self.track_offset_index = 0
        self.play_tempo         = None
        self.play_tempo_preset  = None
        self.track_tempo        = None
        self.track_length       = None
        self.tracks_count       = 0
        self.tracks             = []

        self.title_vertical_offset        = math.ceil((self.BIGGER_LINE_HEIGHT  - self.TITLE_FONT_HEIGHT) / 2.0)
        self.bigger_text_vertical_offset  = math.ceil((self.BIGGER_LINE_HEIGHT  - self.TEXT_FONT_HEIGHT ) / 2.0)
        self.smaller_text_vertical_offset = math.ceil((self.SMALLER_LINE_HEIGHT - self.TEXT_FONT_HEIGHT ) / 2.0)

        self.title_font = ImageFont.truetype('display/display_font.ttf', self.TITLE_FONT_HEIGHT)
        self.text_font  = ImageFont.truetype('display/display_font.ttf', self.TEXT_FONT_HEIGHT )

        self.image  = Image.new("RGB", (LCD_SCREEN_HEIGHT, LCD_SCREEN_WIDTH), self.BACKGROUND_COLOR)
        self.drawer = ImageDraw.Draw(self.image)

        self.play_track_text_width   , height = self.drawer.textsize(self.PLAY_TRACK_TEXT, font = self.text_font)
        self.play_all_text_width     , height = self.drawer.textsize(self.PLAY_ALL_TEXT  , font = self.text_font)
        self.loop_track_text_width   , height = self.drawer.textsize(self.LOOP_TRACK_TEXT, font = self.text_font)
        self.stop_text_width         , height = self.drawer.textsize(self.STOP_TEXT      , font = self.text_font)
        self.tempo_value_width       , height = self.drawer.textsize('123'               , font = self.text_font)
        self.track_length_value_width, height = self.drawer.textsize('12:34'             , font = self.text_font)

        return

    def register_midi_reader(self, midi_reader):

        self.midi_reader  = midi_reader
        self.tracks_count = self.midi_reader.get_files_count()

        for track_index in range(0, self.tracks_count):

            name, tempo, length = self.midi_reader.get_file_info(track_index)

            name_without_ext, ext = os.path.splitext(name)

            length_string = turn_seconds_int_to_minutes_and_seconds_string(length)

            track = {'name' : name_without_ext, 'tempo' : tempo, 'length' : length_string}

            self.tracks.append(track)

        return

    def __get_fill_color__(self, is_inverted):

        if is_inverted == True:
            return self.INVERTED_TEXT_COLOR
        else:
            return self.DEFAULT_TEXT_COLOR

    def __draw_upper_triangle__(self):

        self.drawer.polygon([(LCD_SCREEN_HEIGHT - 15, self.BIGGER_LINE_HEIGHT + 5),
                             (LCD_SCREEN_HEIGHT - 20, self.BIGGER_LINE_HEIGHT + 15),
                             (LCD_SCREEN_HEIGHT - 10, self.BIGGER_LINE_HEIGHT + 15)],
                            fill = self.TRIANGLES_COLOR)

        return

    def __draw_lower_triangle__(self):

        self.drawer.polygon([(LCD_SCREEN_HEIGHT - 15, LCD_SCREEN_WIDTH - 5),
                             (LCD_SCREEN_HEIGHT - 20, LCD_SCREEN_WIDTH - 15),
                             (LCD_SCREEN_HEIGHT - 10, LCD_SCREEN_WIDTH - 15)],
                            fill = self.TRIANGLES_COLOR)

        return

    def __draw_mode_text__(self, mode, is_inverted):

        fill_color = self.__get_fill_color__(is_inverted)

        if mode == MODE.PLAY_ONE_TRACK:

            self.drawer.text((self.HORIZONTAL_MARGIN,
                              self.BIGGER_LINE_HEIGHT * 1 + self.bigger_text_vertical_offset),
                              self.PLAY_TRACK_TEXT,
                              font = self.text_font,
                              fill = fill_color)

        elif mode == MODE.PLAY_ALL_TRACKS:

            self.drawer.text((self.LEFT_PANEL_MID_WIDTH,
                              self.BIGGER_LINE_HEIGHT * 1 + self.bigger_text_vertical_offset),
                              self.PLAY_ALL_TEXT,
                              font = self.text_font,
                              fill = fill_color)

        elif mode == MODE.LOOP_ONE_TRACK:

            self.drawer.text((self.HORIZONTAL_MARGIN,
                              self.BIGGER_LINE_HEIGHT * 2 + self.bigger_text_vertical_offset),
                              self.LOOP_TRACK_TEXT,
                              font = self.text_font,
                              fill = fill_color)

        elif mode == MODE.STOP:

            self.drawer.text((self.LEFT_PANEL_MID_WIDTH,
                              self.BIGGER_LINE_HEIGHT * 2 + self.bigger_text_vertical_offset),
                              self.STOP_TEXT,
                              font = self.text_font,
                              fill = fill_color)

        return

    def __draw_play_tempo_value__(self, tempo_value):

        self.drawer.text((self.LEFT_PANEL_3_4_WIDTH,
                          self.BIGGER_LINE_HEIGHT * 3 + self.SELECTION_MARGIN + self.bigger_text_vertical_offset),
                          str(tempo_value),
                          font = self.text_font,
                          fill = self.DEFAULT_TEXT_COLOR)

        return

    def __draw_track_tempo_value__(self, tempo_value):

        self.drawer.text((self.LEFT_PANEL_3_4_WIDTH,
                          self.BIGGER_LINE_HEIGHT * 4 + self.SELECTION_MARGIN + self.bigger_text_vertical_offset),
                          str(tempo_value),
                          font = self.text_font,
                          fill = self.DEFAULT_TEXT_COLOR)

        return

    def __draw_track_length_value__(self, length_value):

        self.drawer.text((self.LEFT_PANEL_3_4_WIDTH,
                          self.BIGGER_LINE_HEIGHT * 5 + self.SELECTION_MARGIN + self.bigger_text_vertical_offset),
                          length_value,
                          font = self.text_font,
                          fill = self.DEFAULT_TEXT_COLOR)

        return

    def __clear_right_panel__(self):

        self.drawer.rectangle((self.LEFT_PANEL_WIDTH   + 1,
                               self.BIGGER_LINE_HEIGHT + 1,
                               LCD_SCREEN_HEIGHT       - 2,
                               LCD_SCREEN_WIDTH        - 2),
                               fill = self.BACKGROUND_COLOR)

        return

    def __draw_tracks_text__(self, inverted_track_index):

        for display_index in range(0, self.DISPLAY_TRACKS_COUNT):

            track_index = self.track_offset_index + display_index

            if track_index < self.tracks_count:

                if (inverted_track_index is not None) and (inverted_track_index == track_index):
                    self.__draw_track_text__(track_index, display_index, True)
                else:
                    self.__draw_track_text__(track_index, display_index, False)

        # Clear space for navigation triangles
        self.drawer.rectangle((LCD_SCREEN_HEIGHT - self.TRIANGLES_AREA_WIDTH + 1,
                               self.BIGGER_LINE_HEIGHT + 1,
                               LCD_SCREEN_HEIGHT -1,
                               LCD_SCREEN_WIDTH - 1),
                              fill=self.BACKGROUND_COLOR)

        return

    def __draw_track_text__(self, track_index, display_index, is_inverted):

        fill_color = self.__get_fill_color__(is_inverted)

        self.drawer.text((self.LEFT_PANEL_WIDTH   + self.HORIZONTAL_MARGIN,
                          self.BIGGER_LINE_HEIGHT + self.SMALLER_LINE_HEIGHT * display_index + self.smaller_text_vertical_offset),
                          self.tracks[track_index]['name'],
                          font = self.text_font,
                          fill = fill_color)

        return

    def __unset_mode__(self, mode):

        if mode == MODE.PLAY_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN      - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 1 + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN      + self.play_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2),
                                   fill = self.BACKGROUND_COLOR)

            self.__draw_mode_text__(MODE.PLAY_ONE_TRACK, False)

        elif mode == MODE.PLAY_ALL_TRACKS:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH     - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 1 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH     + self.play_all_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 2),
                                   fill = self.BACKGROUND_COLOR)

            self.__draw_mode_text__(MODE.PLAY_ALL_TRACKS, False)

        elif mode == MODE.LOOP_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN      - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN      + self.loop_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 3),
                                   fill = self.BACKGROUND_COLOR)

            self.__draw_mode_text__(MODE.LOOP_ONE_TRACK, False)

        elif mode == MODE.STOP:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH     - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 2 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH     + self.stop_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 3),
                                   fill = self.BACKGROUND_COLOR)

            self.__draw_mode_text__(MODE.STOP, False)

        return

    def preset_mode(self, mode):

        if mode == self.mode_preset:
            return

        log(INFO, 'Display preset mode: {}'.format(mode.name))

        if self.mode_preset != self.mode:
            self.__unset_mode__(self.mode_preset)

        if mode == MODE.PLAY_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN      - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 1 + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN      + self.play_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2),
                                   outline = self.PRESET_COLOR)

        elif mode == MODE.PLAY_ALL_TRACKS:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH     - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 1 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH     + self.play_all_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 2),
                                   outline = self.PRESET_COLOR)

        elif mode == MODE.LOOP_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN      - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN      + self.loop_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 3),
                                   outline = self.PRESET_COLOR)

        elif mode == MODE.STOP:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH     - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 2 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH     + self.stop_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 3),
                                   outline = self.PRESET_COLOR)

        else:

            log(ERROR, 'Got an unsupported mode to preset: {}'.format(mode.name))

        self.lcd_screen.display(self.image)

        self.mode_preset = mode

        return

    def set_mode(self, mode):

        if mode == self.mode:
            return

        log(INFO, 'Display set mode: {}'.format(mode.name))

        self.__unset_mode__(self.mode)

        if mode == MODE.PLAY_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN  - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN  + self.play_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2),
                                   fill = self.SET_COLOR)

            self.__draw_mode_text__(MODE.PLAY_ONE_TRACK, True)

        elif mode == MODE.PLAY_ALL_TRACKS:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH     - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 1 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH     + self.play_all_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 2),
                                   fill = self.SET_COLOR)

            self.__draw_mode_text__(MODE.PLAY_ALL_TRACKS, True)

        elif mode == MODE.LOOP_ONE_TRACK:

            self.drawer.rectangle((self.HORIZONTAL_MARGIN      - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 2 + self.SELECTION_MARGIN,
                                   self.HORIZONTAL_MARGIN      + self.loop_track_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT * 3),
                                   fill = self.SET_COLOR)

            self.__draw_mode_text__(MODE.LOOP_ONE_TRACK, True)

        elif mode == MODE.STOP:

            self.drawer.rectangle((self.LEFT_PANEL_MID_WIDTH     - self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 2 + self.SELECTION_MARGIN,
                                   self.LEFT_PANEL_MID_WIDTH     + self.stop_text_width + self.SELECTION_MARGIN,
                                   self.BIGGER_LINE_HEIGHT   * 3),
                                   fill = self.SET_COLOR)

            self.__draw_mode_text__(MODE.STOP, True)

        else:

            log(ERROR, 'Got an unsupported mode to set: {}'.format(mode.name))

        self.lcd_screen.display(self.image)

        self.mode_preset = mode
        self.mode        = mode

        return

    def preset_track(self, index):

        if index == self.track_preset_index:
            return

        log(INFO, 'Display preset track: {}'.format(self.tracks[index]['name']))

        self.__clear_right_panel__()

        if index < self.track_offset_index:

            self.track_offset_index -= 1

        elif index >= self.track_offset_index + self.DISPLAY_TRACKS_COUNT:

            self.track_offset_index += 1

        preset_display_index = index            - self.track_offset_index
        set_display_index    = self.track_index - self.track_offset_index

        if 0 <= set_display_index <= self.DISPLAY_TRACKS_COUNT - 1:

            self.drawer.rectangle((self.LEFT_PANEL_WIDTH   + self.HORIZONTAL_MARGIN - self.SELECTION_MARGIN ,
                                   self.BIGGER_LINE_HEIGHT + self.SMALLER_LINE_HEIGHT * set_display_index + self.SELECTION_MARGIN ,
                                   LCD_SCREEN_HEIGHT       - self.TRIANGLES_AREA_WIDTH,
                                   self.BIGGER_LINE_HEIGHT + self.SMALLER_LINE_HEIGHT * (set_display_index + 1) + self.SELECTION_MARGIN),
                                   fill = self.PRESET_COLOR)

        self.drawer.rectangle((self.LEFT_PANEL_WIDTH   + self.HORIZONTAL_MARGIN - self.SELECTION_MARGIN ,
                               self.BIGGER_LINE_HEIGHT + self.SMALLER_LINE_HEIGHT * preset_display_index + self.SELECTION_MARGIN ,
                               LCD_SCREEN_HEIGHT       - self.TRIANGLES_AREA_WIDTH,
                               self.BIGGER_LINE_HEIGHT + self.SMALLER_LINE_HEIGHT * (preset_display_index + 1) + self.SELECTION_MARGIN),
                               outline = self.PRESET_COLOR)

        self.__draw_tracks_text__(self.track_index)

        if self.track_offset_index != 0:

            self.__draw_upper_triangle__()

        if self.track_offset_index + self.DISPLAY_TRACKS_COUNT < self.tracks_count:

            self.__draw_lower_triangle__()

        self.lcd_screen.display(self.image)

        self.track_preset_index = index

        return

    def set_track(self, index):

        if index == self.track_index:
            return

        log(INFO, 'Display set track: {}'.format(self.tracks[index]['name']))

        self.__clear_right_panel__()

        set_display_index = index - self.track_offset_index

        self.drawer.rectangle((self.LEFT_PANEL_WIDTH   + self.HORIZONTAL_MARGIN - self.SELECTION_MARGIN ,
                               self.BIGGER_LINE_HEIGHT + self.SMALLER_LINE_HEIGHT * set_display_index + self.SELECTION_MARGIN,
                               LCD_SCREEN_HEIGHT       - self.TRIANGLES_AREA_WIDTH,
                               self.BIGGER_LINE_HEIGHT + self.SMALLER_LINE_HEIGHT * (set_display_index + 1)+ self.SELECTION_MARGIN),
                               fill = self.SET_COLOR)

        self.__draw_tracks_text__(index)

        if self.track_offset_index != 0:

            self.__draw_upper_triangle__()

        if self.track_offset_index + self.DISPLAY_TRACKS_COUNT < self.tracks_count:

            self.__draw_lower_triangle__()

        self.lcd_screen.display(self.image)

        self.track_preset_index = index
        self.track_index        = index

        return

    def __unset_play_tempo__(self):

        self.drawer.rectangle((self.LEFT_PANEL_3_4_WIDTH   - self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 3 + self.SELECTION_MARGIN * 3,
                               self.LEFT_PANEL_3_4_WIDTH   + self.tempo_value_width + self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 4 + self.SELECTION_MARGIN ),
                               fill = self.BACKGROUND_COLOR)

        return

    def __unset_track_tempo__(self):

        self.drawer.rectangle((self.LEFT_PANEL_3_4_WIDTH   - self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 4 + self.SELECTION_MARGIN * 3,
                               self.LEFT_PANEL_3_4_WIDTH   + self.tempo_value_width + self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 5 + self.SELECTION_MARGIN ),
                               fill = self.BACKGROUND_COLOR)

        return

    def __unset_track_length__(self):

        self.drawer.rectangle((self.LEFT_PANEL_3_4_WIDTH   - self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 5 + self.SELECTION_MARGIN * 3,
                               self.LEFT_PANEL_3_4_WIDTH   + self.track_length_value_width + self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 6 + self.SELECTION_MARGIN ),
                               fill = self.BACKGROUND_COLOR)

        return

    def preset_play_tempo(self, tempo):

        if tempo == self.play_tempo_preset:
            return

        log(INFO, 'Display preset play tempo: {}'.format(tempo))

        self.__unset_play_tempo__()

        self.drawer.rectangle((self.LEFT_PANEL_3_4_WIDTH   - self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 3 + self.SELECTION_MARGIN * 3,
                               self.LEFT_PANEL_3_4_WIDTH   + self.tempo_value_width + self.SELECTION_MARGIN,
                               self.BIGGER_LINE_HEIGHT * 4 + self.SELECTION_MARGIN),
                               outline = self.PRESET_COLOR)

        self.__draw_play_tempo_value__(tempo)

        self.lcd_screen.display(self.image)

        self.play_tempo_preset = tempo

        return

    def set_play_tempo(self, tempo):

        if tempo == self.play_tempo:
            return

        log(INFO, 'Display set play tempo: {}'.format(tempo))

        self.__unset_play_tempo__()

        self.__draw_play_tempo_value__(tempo)

        self.lcd_screen.display(self.image)

        self.play_tempo_preset = tempo
        self.play_tempo        = tempo

        return

    def set_track_tempo(self, track_index):

        if track_index == self.track_preset_index:
            return

        tempo = self.tracks[track_index]['tempo' ]

        log(INFO, 'Display set track tempo: {}'.format(tempo))

        self.__unset_track_tempo__()

        self.__draw_track_tempo_value__(tempo)

        self.lcd_screen.display(self.image)

        self.track_tempo = tempo

        return

    def set_track_length(self, track_index):

        if track_index == self.track_preset_index:
            return

        length = self.tracks[track_index]['length' ]

        log(INFO, 'Display set track length: {}'.format(length))

        self.__unset_track_length__()

        self.__draw_track_length_value__(length)

        self.lcd_screen.display(self.image)

        self.track_length = length

        return

    def draw_init(self):

        log(INFO, 'Display draw initialization image: {}'.format(self.INIT_IMAGE))

        self.lcd_screen.module_init()

        file_image = Image.open(self.INIT_IMAGE)

        self.lcd_screen.display(file_image)

        return

    def draw_oper(self):

        log(INFO, 'Display going operational')

        # Draw a simple rectangle around screen
        self.drawer.rectangle((0, 0, LCD_SCREEN_HEIGHT - 1, LCD_SCREEN_WIDTH - 1), outline = 0)

        # Draw Main settings title
        self.drawer.text((self.HORIZONTAL_MARGIN,
                          self.title_vertical_offset),
                          self.SETTINGS_TITLE,
                          font = self.title_font,
                          fill = self.DEFAULT_TEXT_COLOR)

        # Initialize Mode drawing, with no selection
        self.__draw_mode_text__(MODE.PLAY_ONE_TRACK , False)
        self.__draw_mode_text__(MODE.PLAY_ALL_TRACKS, False)
        self.__draw_mode_text__(MODE.LOOP_ONE_TRACK , False)
        self.__draw_mode_text__(MODE.STOP           , False)

        # Draw a horizontal line above Play tempo
        self.drawer.line((0,
                          self.BIGGER_LINE_HEIGHT * 3 + self.SELECTION_MARGIN,
                          self.LEFT_PANEL_WIDTH,
                          self.BIGGER_LINE_HEIGHT * 3 + self.SELECTION_MARGIN),
                          fill = self.LINES_COLOR)

        # Initialize Play tempo drawing, with no value
        self.drawer.text((self.HORIZONTAL_MARGIN,
                          self.BIGGER_LINE_HEIGHT * 3  + self.SELECTION_MARGIN + self.bigger_text_vertical_offset),
                          self.PLAY_TEMPO_TEXT,
                          font = self.text_font,
                          fill = self.DEFAULT_TEXT_COLOR)

        # Draw a horizontal line below Play tempo
        self.drawer.line((0,
                          self.BIGGER_LINE_HEIGHT * 4 + self.SELECTION_MARGIN * 2,
                          self.LEFT_PANEL_WIDTH,
                          self.BIGGER_LINE_HEIGHT * 4 + self.SELECTION_MARGIN * 2),
                          fill = self.LINES_COLOR)

        # Initialize Track tempo drawing, with no value
        self.drawer.text((self.HORIZONTAL_MARGIN,
                          self.BIGGER_LINE_HEIGHT * 4  + self.SELECTION_MARGIN + self.bigger_text_vertical_offset),
                          self.TRACK_TEMPO_TEXT,
                          font = self.text_font,
                          fill = self.DEFAULT_TEXT_COLOR)

        # Initialize Track length drawing, with no value
        self.drawer.text((self.HORIZONTAL_MARGIN,
                          self.BIGGER_LINE_HEIGHT * 5  + self.SELECTION_MARGIN + self.bigger_text_vertical_offset),
                          self.TRACK_LENGTH_TEXT,
                          font = self.text_font,
                          fill = self.DEFAULT_TEXT_COLOR)

        # Draw a vertical line between Main settings & Track selection
        self.drawer.line((self.LEFT_PANEL_WIDTH,
                          0,
                          self.LEFT_PANEL_WIDTH,
                          LCD_SCREEN_WIDTH - 1),
                          fill = self.LINES_COLOR)

        # Draw Track selection title
        self.drawer.text((self.LEFT_PANEL_WIDTH + self.HORIZONTAL_MARGIN,
                          self.title_vertical_offset),
                          self.TRACKS_TITLE,
                          font = self.title_font,
                          fill = self.DEFAULT_TEXT_COLOR)

        # Draw a horizontal line under both titles
        self.drawer.line((0,
                          self.BIGGER_LINE_HEIGHT,
                          LCD_SCREEN_HEIGHT - 1,
                          self.BIGGER_LINE_HEIGHT),
                          fill = self.LINES_COLOR)

        self.lcd_screen.display(self.image)

        # Setup mode, tracks  and tempos with initial values
        self.set_mode (DEFAULT_MODE )
        self.set_play_tempo  (self.tracks[DEFAULT_TRACK]['tempo' ])
        self.set_track_tempo (DEFAULT_TRACK)
        self.set_track_length(DEFAULT_TRACK)
        self.preset_track    (DEFAULT_TRACK)
        self.set_track       (DEFAULT_TRACK)


        return
