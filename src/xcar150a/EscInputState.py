from machine import UART
import time
from src.xcar150a.constants import CommandMessage, get_command_index, command_table

# Based on https://learn.adafruit.com/circuitpython-101-state-machines?view=all


class State(object):
    def __init__(self):
        self.uart: UART = UART(1, baudrate=9600, tx=25, rx=26)

    @property
    def name(self):
        # name get/set
        return ''

    def enter(self, machine):
        # New state at the door
        pass

    def exit(self, machine):
        # To enter the new state, one must have left the old one
        pass

    def update(self, machine, key="", value=""):
        print("ANY?")
        print(self.uart.any())
        print("====")
        if self.uart.any() == 0:
            machine.idle_state = machine.state.name
            machine.idle()
            return False
        return True


class StateMachine(object):
    def __init__(self):
        self.uart: UART = UART(1, baudrate=9600, tx=25, rx=26)
        self.state = None
        self.states = {}
        self.idle_state = None

    # Add states name by definign and calling the class referred to it
    def add_state(self, state):
        self.states[state.name] = state

    # Change state to the one named in the param
    def go_to_state(self, state_name):
        if self.state:
            print('Exiting %s' % (self.state.name))
            self.state.exit(self)
        self.state = self.states[state_name]
        print('Entering %s' % (self.state.name))
        self.state.enter(self)

    # Just passing values to the right update handler
    def update(self, key, value):
        if self.state:
            print('Updating %s' % (self.state.name))
            self.state.update(self, key, value)

    def idle(self):
        self.state = self.states['idle']
        print('Idle')
        self.state.enter(self)


class IdleState(State):
    @property
    def name(self):
        return 'idle'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine: StateMachine, key="", value=""):
        if (State.update(self, machine, key, value)):
            if (key == 'speed'):
                machine.go_to_state('speed')
            else:
                machine.go_to_state('ready')


class SpeedState(State):
    @property
    def name(self):
        return 'speed'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine: StateMachine, key="", value=""):
        if (State.update(machine, key, value)):
            self.uart.write("S")
            time.sleep_ms(100)
            self.uart.write(value)
            time.sleep_ms(100)
            machine.go_to_state('idle')


class ReadyState(State):
    @property
    def name(self):
        return 'ready'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine, key="", value=""):
        if (State.update(self, machine, key, value)):
            self.uart.write('T')  # random char to start conversation
            time.sleep_ms(1000)
            machine.go_to_state('on_going')
        else:
            machine.go_to_state('idle')


class OnGoingState(State):
    @property
    def name(self):
        return 'on_going'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine: StateMachine, key="", value=""):
        if (State.update(self, machine, key, value)):
            command_message_index = get_command_index(key)
            command_message: CommandMessage = command_table.get(
                command_message_index)
            label_index = command_message.get_label_table_value(value)
            self.uart.write(command_message_index)
            time.sleep_ms(1000)
            self.uart.write(label_index)
            time.sleep_ms(100)
            machine.go_to_state('completed')


class CompletedState(State):
    @property
    def name(self):
        return 'completed'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine: StateMachine, key="", value=""):
        machine.go_to_state("idle")
