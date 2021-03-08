import psutil


def clamp(value, minimum, maximum):

    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    else:
        return value


def is_process_running(name):

    for process in psutil.process_iter():
        try:
            if name == process.name():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return False;


def turn_seconds_int_to_minutes_and_seconds_string(seconds_int):

    seconds = int(seconds_int % 60)
    minutes = int(seconds_int / 60)

    return '{:02}:{:02}'.format(minutes, seconds)


def truncate_and_format_string(input_string, max_length):

    if len(input_string) > max_length:

        output_string = input_string[:max_length - 3] + '...'

    else:

        output_string = input_string

        while len(output_string) < max_length:
            output_string += ' '

    return output_string
