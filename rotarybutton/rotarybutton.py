import encoder

from log import *


class RotaryButton:

    TURNED_TO_THE_LEFT  = -1
    DID_NOT_TURN        = 0
    TURNED_TO_THE_RIGHT = 1

    def __init__(self, name, gpio_interface, encoder_pin_1, encoder_pin_2, encoder_pin_press):

        log(INFO, 'Setting up {} basic  rotary button: {} / {} / {}'.format(name, encoder_pin_1, encoder_pin_2, encoder_pin_press))

        self.name              = name
        self.encoder           = encoder.Encoder(name, gpio_interface, encoder_pin_1, encoder_pin_2, encoder_pin_press)
        self.last_position     = 0;
        self.last_press_status = False

    def get_value(self):

        return self.encoder.get_counter()

    def get_move(self):

        current_position = self.get_value()

        if current_position > self.last_position:
            return_value = self.TURNED_TO_THE_RIGHT
        elif current_position < self.last_position:
            return_value = self.TURNED_TO_THE_LEFT
        else:
            return_value = self.DID_NOT_TURN

        self.last_position = current_position

        return return_value

    def is_pressed(self):

        return self.encoder.is_pressed()

    def is_released(self):

        return not self.encoder.is_pressed()

    def was_clicked(self):

        current_press_status = self.is_pressed()

        if (self.last_press_status == True) and (current_press_status == False):
            return_value = True
        else:
            return_value = False

        self.last_press_status = current_press_status

        return return_value


class RotaryStatesButton(RotaryButton):

    def __init__(self, name, gpio_interface, encoder_pin_1, encoder_pin_2, encoder_pin_press, states_list, loop_over_states):

        log(INFO, 'Setting up {} states rotary button: {} / {}'.format(name, states_list, loop_over_states))

        self.name             = name
        self.states_list      = states_list
        self.loop_over_states = loop_over_states
        self.states_count     = len(states_list)
        self.state_index      = 0

        super().__init__(name, gpio_interface, encoder_pin_1, encoder_pin_2, encoder_pin_press)

    def get_move(self):

        raise NotImplementedError("get_move() function not implemented for states rotary button. get_state() shall be used instead.")

    def set_state(self, state):

        if state not in self.states_list:

            log(WARNING, 'Input state ({}) not in states lists; using 1st state instead'.format(state))
            self.state_index = 0

        else:

            self.state_index = self.states_list.index(state)
            log(DEBUG, 'Setting {} button state to value: {}'.format(self.name, state))

    def get_state(self):

        current_move = super().get_move()

        if current_move == self.TURNED_TO_THE_LEFT:
            self.state_index -= 1
        elif current_move == self.TURNED_TO_THE_RIGHT:
            self.state_index += 1
        else:
            # Button did not turn
            pass

        if self.loop_over_states == True:

            self.state_index %= self.states_count

        else:

            if self.state_index >= self.states_count:
                self.state_index = self.states_count - 1
            elif self.state_index < 0:
                self.state_index = 0

        return self.states_list[self.state_index]
