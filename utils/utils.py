import psutil


NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def clamp(value, minimum, maximum):

    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    else:
        return value


def get_note_name_from_midi_number(midi_number):
    
    return NOTE_NAMES[midi_number % 12] + str((int(midi_number / 12) - 1))


def is_process_running(name):

    for process in psutil.process_iter():
        try:
            if name == process.name():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return False;

