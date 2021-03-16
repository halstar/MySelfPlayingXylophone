import os
import sys

from mido import MidiFile, MidiTrack, MetaMessage, Message, second2tick, bpm2tempo


sys.path.append("..")

from optparse import OptionParser
from log      import *
from utils    import *

VERSION          = '1.0'
UPDATE_DATE      = '2021-03-05'
VERSION_STRING   = '%%prog v%s (%s)' % (VERSION, UPDATE_DATE)
USAGE            = 'usage: %prog [-h] [--verbose=INT] (--src-dir=STRING | --src-file=STRING) (--dst-dir=STRING | --dry-run) ' \
                   '--min-note=INT --num-notes=INT [--min-length=INT] [--max-sim-notes=INT] [--do-transpose] [--remove-src]'
LONG_DESCRIPTION = 'This program analyses, filters & rewrites a MIDI file or directory of MIDI files to select/rearrange file(s) matching given criterias.'

# Default values for options
DEFAULT_LOG_LEVEL  = INFO
DEFAULT_SIM_NOTES  = 10
DEFAULT_MIN_LENGTH = 10

# Other constants
STATUS_FILENAME_LENGTH      = 16
OUTPUT_MIDI_FILE_TYPE       =  1
OUTPUT_MIDI_FILE_INSTRUMENT =  9
OUTPUT_MIDI_FILE_VELOCITY   = 64

COLOR_RED   = '\033[31m'
COLOR_GREEN = '\033[32m'
COLOR_END   = '\033[0m'

# Minimum required version of Python interpreter
REQUIRED_PYTHON_VERSION = 3


def main():

    # Get input options
    argv = sys.argv[1:]

    # Check python version is the minimum expected one
    if sys.version_info[0] < REQUIRED_PYTHON_VERSION:

        log(ERROR, 'This tool requires at least Python version {}'.format(REQUIRED_PYTHON_VERSION))
        sys.exit(3)

    # Setup options parser
    try:

        parser = OptionParser(usage   = USAGE,
                              version = VERSION_STRING,
                              epilog  = LONG_DESCRIPTION)

        parser.add_option('-v',
                          '--verbose',
                          action  = 'store',
                          dest    = 'verbose',
                          help    = 'Optional - Set verbose level [default: %default]',
                          metavar = 'STRING')

        parser.add_option('-s',
                          '--src-dir',
                          action  = 'store',
                          dest    = 'src_dir',
                          help    = 'Optional - Set the source directory, holding MIDI files',
                          metavar = 'STRING')

        parser.add_option('-f',
                          '--src-file',
                          action  = 'store',
                          dest    = 'src_file',
                          help    = 'Optional - Select one source MIDI file',
                          metavar = 'STRING')

        parser.add_option('-d',
                          '--dst-dir',
                          action  = 'store',
                          dest    = 'dst_dir',
                          help    = 'Optional - Set the destination directory, holding MIDI file(s) out of filtering',
                          metavar = 'STRING')

        parser.add_option('-y',
                          '--dry-run',
                          action  = 'store_true',
                          default = False,
                          dest    = 'is_dry_run',
                          help    = 'Optional - Do not apply filtering; just show up what could be done')

        parser.add_option('-m',
                          '--min-note',
                          action  = 'store',
                          dest    = 'min_note',
                          help    = 'Mandatory - Minimum/lowest note MIDI value',
                          metavar = 'INT')

        parser.add_option('-n',
                          '--num-notes',
                          action  = 'store',
                          dest    = 'num_notes',
                          help    = 'Mandatory - Number of notes, starting from minimum/lowest note',
                          metavar = 'INT')

        parser.add_option('-l',
                          '--min-length',
                          action  = 'store',
                          dest    = 'min_length',
                          help    = 'Optional - Minimum expected output length, in seconds. Set to 0 for file full length [default: %default]',
                          metavar = 'INT')

        parser.add_option('-x',
                          '--max-sim-notes',
                          action  = 'store',
                          dest    = 'max_sim_notes',
                          help    = 'Optional - Maximum notes allowed to be played simultaneously [default: %default]',
                          metavar = 'INT')

        parser.add_option('-t',
                          '--do-transpose',
                          action  = 'store_true',
                          default = False,
                          dest    = 'do_transpose',
                          help    = 'Optional - Try and transpose file(s) to better fit into input notes range')


        parser.add_option('-r',
                          '--remove-src',
                          action  = 'store_true',
                          default = False,
                          dest    = 'remove_src',
                          help    = 'Optional - Once written to the destination directory, remove source file(s) that matched filtering')

        # Set options defaults
        parser.set_defaults(verbose       = DEFAULT_LOG_LEVEL )
        parser.set_defaults(min_length    = DEFAULT_MIN_LENGTH)
        parser.set_defaults(max_sim_notes = DEFAULT_SIM_NOTES )

        # Actually process input options
        try:
            (opts, args) = parser.parse_args(argv)
        except SystemExit:
            return 3

        criteria = {}

        # Check the mandatory options
        if not opts.min_note:
            log(ERROR , 'Missing input mandatory option --min-note. Try --help')
            return 3

        criteria['min_note'] = opts.min_note

        if not opts.num_notes:
            log(ERROR , 'Missing input mandatory option --num-notes. Try --help')
            return 3

        criteria['num_notes'] = opts.num_notes

        # Check the input/output options
        if not opts.src_dir and not opts.src_file:
            log(ERROR , '--src-dir or --src-file shall be provided. Try --help')
            return 3

        if not opts.dst_dir and not opts.is_dry_run:
            log(ERROR , '--dst-dir or --dry-run shall be provided. Try --help')
            return 3

        if opts.remove_src and not opts.dst_dir:
            log(ERROR , 'To use --remove-src, --dst-dir shall be provided. Try --help')
            return 3

        # Check directories/files existence
        if opts.src_dir and not os.path.isdir(opts.src_dir):
            log(ERROR, '{} directory not found'.format(opts.src_dir))
            return 3

        if opts.dst_dir and not os.path.isdir(opts.dst_dir):
            log(ERROR, '{} directory not found'.format(opts.dst_dir))
            return 3

        if opts.src_file and not os.path.isfile(opts.src_file):
            log(ERROR, '{} file not found'.format(opts.src_file))
            return 3

        # Deal with other filtering options
        criteria['is_dry_run'   ] = opts.is_dry_run
        criteria['do_transpose' ] = opts.do_transpose
        criteria['lowest_note'  ] = int(opts.min_note)
        criteria['highest_note' ] = int(opts.min_note) + int(opts.num_notes) - 1
        criteria['num_notes'    ] = int(opts.num_notes    )
        criteria['min_length'   ] = int(opts.min_length   )
        criteria['max_sim_notes'] = int(opts.max_sim_notes)

        log_set_level(int(opts.verbose))

    except Exception as error:

        log(ERROR, 'Unexpected parsing error. Try --help')
        log(ERROR, '{}'.format(error))
        return 3

    # Options are OK: process with the test
    os.system('clear')

    log(INFO, '*********************************')
    log(INFO, '* Starting MIDI files filtering *')
    log(INFO, '*********************************')
    log(INFO, '')
    log(INFO, 'Initiating...')
    log(INFO, '')
    log(DEBUG, 'is_dry_run    = {}'.format(criteria['is_dry_run'   ]))
    log(DEBUG, 'do_transpose  = {}'.format(criteria['do_transpose' ]))
    log(DEBUG, 'lowest_note   = {}'.format(criteria['lowest_note'  ]))
    log(DEBUG, 'highest_note  = {}'.format(criteria['highest_note' ]))
    log(DEBUG, 'min_length    = {}'.format(criteria['min_length'   ]))
    log(DEBUG, 'max_sim_notes = {}'.format(criteria['max_sim_notes']))
    log(DEBUG, 'Lowest  note: {}'.format(get_note_name_from_midi_number(criteria['lowest_note'  ])))
    log(DEBUG, 'Highest note: {}'.format(get_note_name_from_midi_number(criteria['highest_note' ])))

    if opts.src_file:

        is_status_ok = True

        fullname_with_ext         = opts.src_file
        filename_with_ext         = os.path.basename(fullname_with_ext)
        filename_without_ext, ext = os.path.splitext(filename_with_ext)

        try:

            input_midi_data = MidiFile(fullname_with_ext, clip = True)

        except Exception as error:

            is_status_ok = False

            log(WARNING, 'Could not load {}; file might be corrupt'.format(fullname_with_ext))
            log(WARNING, error)

        output_midi_data = MidiFile(type = OUTPUT_MIDI_FILE_TYPE, clip = True)

        if is_status_ok:

            is_status_ok, msg_count, transpose_offset = analyze_file(input_midi_data, filename_without_ext, criteria, output_midi_data)

        if is_status_ok and not opts.is_dry_run:

            output_fullname_with_ext = os.path.join(opts.dst_dir, filename_with_ext)

            write_output_file(output_midi_data, output_fullname_with_ext, msg_count, transpose_offset)

            if opts.remove_src:

                remove_input_file(fullname_with_ext)

    else:

        for dirname, dirnames, filenames in os.walk(opts.src_dir):

            for filename_with_ext in filenames:

                is_status_ok = True

                fullname_with_ext         = os.path.join    (dirname, filename_with_ext)
                filename_without_ext, ext = os.path.splitext(filename_with_ext         )

                try:

                    input_midi_data = MidiFile(fullname_with_ext, clip = True)

                except Exception as error:

                    is_status_ok = False

                    log(WARNING, 'Could not load {}; file might be corrupt'.format(fullname_with_ext))
                    log(WARNING, error)

                output_midi_data = MidiFile(type = OUTPUT_MIDI_FILE_TYPE, clip = True)

                if is_status_ok:

                    is_status_ok, msg_count, transpose_offset = analyze_file(input_midi_data, filename_without_ext, criteria, output_midi_data)

                if is_status_ok and not opts.is_dry_run:

                    output_fullname_with_ext = os.path.join(opts.dst_dir, filename_with_ext)

                    write_output_file(output_midi_data, output_fullname_with_ext, msg_count, transpose_offset)

                    if opts.remove_src:

                        remove_input_file(fullname_with_ext)

    log(INFO, '')
    log(INFO, 'Exiting...')
    log(INFO, '')
    log(INFO, '************************************')
    log(INFO, '*  Done with MIDI files filtering  *')
    log(INFO, '************************************')

    return 0


def analyze_file(input_midi_data, input_filename, criteria, output_midi_data):

    log(INFO, 'Analyzing input: {}'.format(input_filename))

    summed_length             = 0
    last_written_notes_time   = 0
    max_length_no_transpose   = 0
    max_length_with_transpose = 0
    lowest_note               = -1
    highest_note              = -1
    transpose_offset          = 0
    transpose_range           = 0
    msg_count                 = 0
    msg_count_no_transpose    = 0
    msg_count_with_transpose  = 0

    is_format_ok                = True
    is_file_too_short           = False
    is_max_sim_notes_passed     = False
    is_no_transpose_scan_done   = False
    is_with_transpose_scan_done = False
    is_expected_length_check_ok = True
    is_global_status_ok         = True

    # Get detailed necessary information from input MIDI data
    try:

        file_length    =                               int(input_midi_data.length)
        tempo_in_bpm   = midi.get_midi_file_tempo         (input_midi_data)
        events         = midi.get_midi_file_events        (input_midi_data)
        ticks_per_beat = midi.get_midi_file_ticks_per_beat(input_midi_data)

    except Exception as error:

        is_format_ok = False
        file_length  = 0

        log(WARNING, 'Could not parse {}; file might be corrupt'.format(input_filename))
        log(WARNING, error)

    # Prepare filtering based on length
    if criteria['min_length'] == 0:
        expected_min_length = file_length
    else:
        expected_min_length = criteria['min_length']

    file_length_string         = turn_seconds_int_to_minutes_and_seconds_string(file_length        )
    expected_min_length_string = turn_seconds_int_to_minutes_and_seconds_string(expected_min_length)

    # In case of a corrupt file, let's just stop with that fle
    if is_format_ok:

        # Check general file format
        if input_midi_data.type == 2:

            log(WARNING, 'Unsupported MIDI file type 2')
            is_format_ok = False

        if tempo_in_bpm == 0:

            log(WARNING, 'No valid tempo was found in file')
            is_format_ok = False

        if len(events) == 0:

            log(WARNING, 'No events were found in file!')
            is_format_ok = False

        if ticks_per_beat == 0:

            log(WARNING, 'No valid ticks per beat data was found in file')
            is_format_ok = False

    # In case of a bad/unsupported format, let's just stop with that fle
    if is_format_ok:

        tempo_in_midi  = bpm2tempo(tempo_in_bpm)

        # Initialize output MIDI data
        output_midi_data.ticks_per_beat = ticks_per_beat
        output_track = MidiTrack()
        output_track.append(Message    ('program_change', program = OUTPUT_MIDI_FILE_INSTRUMENT, time = 0))
        output_track.append(MetaMessage('set_tempo'     , tempo   = tempo_in_midi              , time = 0))
        msg_count += 2

        log(DEBUG, 'Tempo: {} / Length: {} / #Events: {}'.format(tempo_in_bpm, file_length_string, len(events)))

        # Check file overall length against expected minimum length
        if file_length < expected_min_length:

            log(WARNING, 'Overall file length, {}, is lower than expected minimum length, {}'.format(file_length_string, expected_min_length_string))
            is_file_too_short = True

        # Start browsing file events
        for event in events:

            if event['type'] == IS_PAUSE:

                pause = event['value']

                summed_length += pause

                if not is_no_transpose_scan_done:

                    max_length_no_transpose += pause

                if not is_with_transpose_scan_done:

                    max_length_with_transpose += pause

            else:

                notes = event['value']

                if len(notes) > criteria['max_sim_notes']:

                    log(WARNING, 'Maximum simultaneous notes count passed: {}'.format(len(notes)))
                    is_max_sim_notes_passed = True

                is_first_note_in_notes = True

                for note in notes:

                    # Memorize highest and lowest notes ever found from the start of that file; this is used to transpose
                    if lowest_note == -1:
                        lowest_note  = note
                        highest_note = note
                    elif note < lowest_note:
                        lowest_note = note
                    elif note > highest_note:
                        highest_note = note

                    if is_first_note_in_notes:

                        # Add delay prior to playing those notes
                        notes_delta_time_in_ticks = int(second2tick(summed_length - last_written_notes_time, ticks_per_beat, tempo_in_midi))

                        is_first_note_in_notes = False

                    else:

                        # Other notes shall play at the same time as the first note
                        notes_delta_time_in_ticks = 0

                    if not(criteria['lowest_note'] <= note <= criteria['highest_note']):

                        log(DEBUG, 'Note {} out of range [{}-{}]'.format(note, criteria['lowest_note'], criteria['highest_note']))

                        if not is_no_transpose_scan_done:

                            is_no_transpose_scan_done = True
                            msg_count_no_transpose    = msg_count

                            log(INFO, 'Done with scan with no transpose - Got partial content')

                    if not(highest_note - lowest_note + 1 <= criteria['num_notes']):

                        log(DEBUG, 'Note {} out of range, even with transpose'.format(note))

                        if not is_with_transpose_scan_done:

                            is_with_transpose_scan_done = True
                            msg_count_with_transpose    = msg_count

                            log(INFO, 'Done with scan with    transpose - Got partial content')

                            # No need to analyze file any further
                            break

                    else:

                        # Compute output transpose offset and transpose_range, as long as note track range fits within available number of notes
                        transpose_offset = criteria['lowest_note'] - lowest_note
                        transpose_range  = highest_note - lowest_note + 1

                    output_track.append(Message('note_on' , note = note, velocity = OUTPUT_MIDI_FILE_VELOCITY, time = notes_delta_time_in_ticks))
                    msg_count += 1

                last_written_notes_time = summed_length

        # End of file reached & all file fitted in with no transpose
        if not is_no_transpose_scan_done:

            msg_count_no_transpose = msg_count

            log(INFO, 'Done with scan with no transpose - Got full    content')

        # End of file reached & all file fitted in with transpose
        if not is_with_transpose_scan_done:

            msg_count_with_transpose = msg_count

            log(INFO, 'Done with scan with    transpose - Got full    content')

        log(DEBUG, 'Scanned notes range = [{}-{}]'.format(lowest_note, highest_note))

        # Finalize output MIDI data
        output_midi_data.tracks.append(output_track)

    # Check expected minimum length criteria
    if not criteria['do_transpose'] and max_length_no_transpose < expected_min_length:

        is_expected_length_check_ok = False

    elif criteria['do_transpose'] and max_length_with_transpose < expected_min_length:

        is_expected_length_check_ok = False

    # Compute final/global file status
    if not is_format_ok or is_file_too_short or is_max_sim_notes_passed or not is_expected_length_check_ok:

        is_global_status_ok = False

    # Print out a synthetic line per file, showing up analysis detailed status
    if is_global_status_ok:
        print(COLOR_GREEN, end = '', flush = True)
    else:
        print(COLOR_RED  , end = '', flush = True)

    print('{}'.format(truncate_and_format_string(input_filename, STATUS_FILENAME_LENGTH)) + COLOR_END +  ' - ', end = '', flush = True)

    if is_format_ok:
        print('Format: OK', end = '', flush = True)
    else:
        print(COLOR_RED + 'Format: KO' + COLOR_END, end = '', flush = True)

    print(' - File length: {} - '.format(file_length_string), end = '', flush = True)

    if not is_file_too_short:
        print('Short file check: OK', end = '', flush = True)
    else:
        print(COLOR_RED + 'Short file check: KO' + COLOR_END, end = '', flush = True)

    print(' - ', end = '', flush = True)

    if not is_max_sim_notes_passed:
        print('Max sim notes check: OK', end = '', flush = True)
    else:
        print(COLOR_RED + 'Max sim notes check: KO' + COLOR_END, end = '', flush = True)

    max_length_no_transpose_string   = turn_seconds_int_to_minutes_and_seconds_string(max_length_no_transpose  )
    max_length_with_transpose_string = turn_seconds_int_to_minutes_and_seconds_string(max_length_with_transpose)

    print(' - Max length no transpose: {}'.format     (max_length_no_transpose_string  ), end = '', flush = True)
    print(' - Max length with transpose: {} - '.format(max_length_with_transpose_string), end = '', flush = True)

    if is_expected_length_check_ok:
        print('Expected length check: OK', end = '', flush = True)
    else:
        print(COLOR_RED + 'Expected length check: KO' + COLOR_END, end = '', flush = True)

    print('')

    # Try some post-processings on transposition, for the sake of a good sound
    if is_global_status_ok and criteria['do_transpose'] and (transpose_offset != 0):

        log(INFO, 'Transpose range : {}'.format(transpose_range))
        log(INFO, 'Transpose offset: {}'.format(transpose_offset))

        align_lowest_note_offset = 12 - (criteria['lowest_note'] % 12) + (lowest_note % 12)

        # Try and transpose by having the lowest note identical to the original, but on another
        # octave, so that the transposition will actually sound much closer to the original.
        if align_lowest_note_offset + transpose_range <= criteria['num_notes']:

            print("Before fix ", lowest_note, highest_note, transpose_offset, align_lowest_note_offset)
            transpose_offset += align_lowest_note_offset
            log(INFO, "Could apply octave    correction on transpose offset, now: {}".format(transpose_offset))
            print("After fix  ", transpose_offset, lowest_note + transpose_offset,  highest_note + transpose_offset,)

        # If transpose offset is odd (i.e. a half-tone) and we got room to make it even (i.e. full tone),
        # let's go for an even offset, by adding 1 half-tone: full tone transposition should sound better.
        elif (transpose_offset % 2 != 0) and (transpose_range <= criteria['num_notes'] - 1):

            transpose_offset += 1
            log(INFO, "Could apply full tone correction on transpose offset, now: {}".format(transpose_offset))

    if not criteria['do_transpose']:

        return is_global_status_ok, msg_count_no_transpose, 0

    else:

        return is_global_status_ok, msg_count_with_transpose, transpose_offset


def write_output_file(output_midi_data, output_fullname, msg_count, transpose_offset):

    filename_with_ext         = os.path.basename(output_fullname)
    filename_without_ext, ext = os.path.splitext(filename_with_ext)

    log(INFO, 'Writing   output: {}'.format(filename_without_ext))

    # If necessary, truncate last (out of range) messages in the single track we created
    del output_midi_data.tracks[0][msg_count:]

    # Add an End of track message, some little time after the very last note
    # (needed to hear this last note being played, while previewing on a local PC)
    output_midi_data.tracks[0].append(MetaMessage('end_of_track', time = 100))

    # If necessary, transpose all notes in the single track we created
    if transpose_offset != 0:

        for msg in output_midi_data.tracks[0]:
            if msg.type in ['note_on']:
                msg.note += transpose_offset

    # Actually save file
    output_midi_data.save(output_fullname)

    return


def remove_input_file(input_fullname):

    filename_with_ext         = os.path.basename(input_fullname)
    filename_without_ext, ext = os.path.splitext(filename_with_ext)

    log(INFO, 'Removing  input {}'.format(filename_without_ext))

    os.remove(input_fullname)

    return


def graceful_exit(return_code):

    os._exit(return_code)

    return


if __name__ == '__main__':

    try:

        log_init(ERROR)

        main_status = main()

        graceful_exit(main_status)

    except KeyboardInterrupt:
        log(ERROR, 'Keyboard interrupt...')
        graceful_exit(1)

    except Exception as error:
        log(ERROR, 'Error: ' + str(error))
        graceful_exit(2)
