from micropython import const
import array as arr

percentBrakingLabel = dict(
    _percent_10=const(0), _percent_20=const(1), _percent_30=const(2),
    _percent_40=const(3), _percent_50=const(4), _percent_60=const(5),
    _percent_70=const(6), _percent_80=const(7), _percent_100=const(8)
)
percentDragBrakeLabel = dict(
    _percent_0=const(0), _percent_4=const(1), _percent_8=const(2),
    _percent_12=const(3), _percent_15=const(4), _percent_20=const(5),
    _percent_25=const(6), _percent_30=const(7)
)
throttleLimitLabel = dict(
    _percent_0=const(0), _percent_20=const(1), _percent_30=const(2),
    _percent_40=const(3), _percent_50=const(4), _percent_60=const(5),
    _percent_70=const(6), _percent_80=const(7), _percent_90=const(8)
)
perCentThrottleReverseLabel = dict(
    _percent_20=const(0), _percent_30=const(1), _percent_40=const(2),
    _percent_50=const(3), _percent_60=const(4), _percent_70=const(5),
    _percent_80=const(6), _percent_90=const(7), _percent_100=const(8)
)
neutralRangeLabel = dict(
    _percent_2=const(0), _percent_3=const(1), _percent_5=const(2), _percent_6=const(3)
)

cutOffVoltageLabel = dict(
    _per_cell_2_6=const(0), _per_cell_2_8=const(1), _per_cell_3_0=const(2),
    _per_cell_3_2=const(3), _per_cell_3_4=const(4), _no_cut_off=const(5)
)

runningModeLabel = dict(
    _forward_only=const(0), _fwd_pse_rev=const(1), _fwd_rev=const(2)
)

motorRotationLabel = dict(_normal=const(0), _reverse=const(1))

initialAccelerationLabel = dict(
    low=const(0), medium=const(1), high=const(2), very_high=const(3)
)

motorTimingLabel = dict(
    very_low=const(0), low=const(1), normal=const(2), high=const(3), very_high=const(4)
)

becOutputLabel = dict(_v_6_0=const(0), _v_8_4=const(1))


class CommandMessage:
    label_table: dict

    def __init__(self, label_table: dict):
        self.label_table = label_table

    def get_label_table_value(self, key):
        return self.label_table[key]

    def __key(self):
        return (self.label_table)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, CommandMessage):
            return self.__key() == other.__key()
        return NotImplemented

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)


command_table: dict[int, CommandMessage] = {
    # Code[2], DefArg, ExpRespLength, LabelTable #
    0: CommandMessage(None),
    1: CommandMessage(cutOffVoltageLabel),
    2: CommandMessage(throttleLimitLabel),
    3: CommandMessage(percentBrakingLabel),
    4: CommandMessage(initialAccelerationLabel),
    5: CommandMessage(motorTimingLabel),
    6: CommandMessage(motorRotationLabel),
    7: CommandMessage(percentDragBrakeLabel),
    8: CommandMessage(neutralRangeLabel),
    9: CommandMessage(runningModeLabel),
    10: CommandMessage(perCentThrottleReverseLabel),
    11: CommandMessage(becOutputLabel),
    12: CommandMessage(None)
}


class Command:
    CMD_ESC_GET_INIT_CFG = '_'
    CMD_ESC_SET_CUT_OFF_V = 'A'
    CMD_ESC_SET_THROTTLE_LIM = 'B'
    CMD_ESC_SET_PC_BREAKING = 'C'
    CMD_ESC_SET_PC_INITIAL_ACC = 'D'
    CMD_ESC_SET_MOTOR_TIMING = 'E'
    CMD_ESC_SET_MOTOR_ROTATION = 'F'
    CMD_ESC_SET_PC_DRAG_BREAK = 'G'
    CMD_ESC_SET_NEUTRAL_RANGE = 'H'
    CMD_ESC_SET_RUNNING_MODE = 'I'
    CMD_ESC_SET_PC_REV_THROTTLE = 'J'
    CMD_ESC_SET_BEC_OUTPUT = 'K'
    CMD_ESC_GET_CUR_CFG = ''


def get_command_index(key) -> int:
    if (key == "cutoff_voltage"):
        return Command.CMD_ESC_SET_CUT_OFF_V
    elif(key == "throttle_limit"):
        return Command.CMD_ESC_SET_THROTTLE_LIM
    elif(key == "percent_braking"):
        return Command.CMD_ESC_SET_PC_BREAKING
    elif(key == "initial_acc"):
        return Command.CMD_ESC_SET_PC_INITIAL_ACC
    elif(key == "motor_timing"):
        return Command.CMD_ESC_SET_MOTOR_TIMING
    elif(key == "motor_rotation"):
        return Command.CMD_ESC_SET_MOTOR_ROTATION
    elif(key == "percent_drag_brake"):
        return Command.CMD_ESC_SET_PC_DRAG_BREAK
    elif(key == "neutral_range"):
        return Command.CMD_ESC_SET_NEUTRAL_RANGE
    elif(key == "running_mode"):
        return Command.CMD_ESC_SET_RUNNING_MODE
    elif(key == "percent_throttle_reverse"):
        return Command.CMD_ESC_SET_PC_REV_THROTTLE
    elif(key == "bec_output"):
        return Command.CMD_ESC_SET_BEC_OUTPUT
    elif(key == "current_config"):
        return Command.CMD_ESC_GET_CUR_CFG
