from mido import tempo2bpm

IS_PAUSE   = 0
IS_NOTES   = 1
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
TEMPO_LIST = [30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 63, 66, 69, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112,
              116, 120, 126, 132, 138, 144, 152, 160, 168, 176, 184, 192, 200]


def get_note_name_from_midi_number(midi_number):

    return NOTE_NAMES[midi_number % 12] + str((int(midi_number / 12) - 1))


def get_midi_file_ticks_per_beat(midi_file_data):

    return midi_file_data.ticks_per_beat


def get_midi_file_tempo(midi_file_data):

    raw_tempo = 0

    for track_index, track_data in enumerate(midi_file_data.tracks):

        for msg in track_data:

            if (msg.is_meta == True) and (msg.type == 'set_tempo') and (msg.tempo != 0):
                raw_tempo = int(tempo2bpm(msg.tempo))
                break

    if raw_tempo == 0:

        tempo = 0

    elif raw_tempo < TEMPO_LIST[0]:

        tempo = TEMPO_LIST[0]

    elif raw_tempo > TEMPO_LIST[-1]:

        tempo = TEMPO_LIST[-1]

    else:

        for allowed_tempo in TEMPO_LIST:

            # Return tempo value if found in list or round to the first closest/lower allowed value
            if (allowed_tempo == raw_tempo) or (allowed_tempo > raw_tempo):

                tempo = allowed_tempo
                break

            else:

                # Just move on to next tempo value in list
                pass

    return tempo


def get_midi_file_events(midi_file_data):

    events = []

    for msg in midi_file_data:

        if msg.time != 0:

            if len(events) != 0 and events[-1]['type'] == IS_PAUSE:
                events[-1]['value'] += msg.time
            else:
                events.append({'type' : IS_PAUSE,
                               'value': msg.time})

        if msg.type == 'note_on' or msg.type == 'note_off':

            if msg.velocity != 0:

                if len(events) != 0 and events[-1]['type'] == IS_NOTES:
                    events[-1]['value'].append(msg.note)
                else:
                    events.append({'type' : IS_NOTES,
                                   'value': [msg.note]})

    # Post process events
    for event in events:

        if event['type'] == IS_NOTES:
            # Remove duplicate notes, if any (consider the case of
            # several instruments playing the note at the same time)
            event['value'] = list(set(event['value']))

            # Order notes ascending (for debug readability & possible truncation)
            event['value'].sort()

    return events
