from networking import SenderReceiver, Logger, do_nothing, Server, SERVER_PORT
from joystick import Joystick

try:
    import serial
except ModuleNotFoundError:
    import pip

    pip.main(['install', 'pyserial'])
finally:
    import serial

COM_PORT = '/dev/ttyACM0'
DATA_RATE_BPS = 9600

AXIS_MULTIPLIER = 1000
AXIS_DIGITS_COUNT = 4

logger = Logger(do_nothing)


def get_sendable_axis_value(value):
    is_positive = True
    value = float(value)
    if value < 0:
        value = -value
        is_positive = False
    value = int(value * AXIS_MULTIPLIER)
    value_str = str(value)
    padding_size = AXIS_DIGITS_COUNT - len(value_str)
    value_str = '0' * padding_size + value_str
    value_str = ('+' if is_positive else '-') + value_str
    return value_str


def get_sendable_button_value(value):
    return str(value)  # just '0' or '1'


def get_number_with_sign_str(num):
    res = ''
    if num >= 0:
        return '+' + str(num)
    return str(num)


def get_sendable_hat_value(value):
    # value is a tuple in the form (x, x) where
    # x can be 1, 0 or -1.
    # the value 0 will be considered positive to
    # count for fewer cases.

    result = ''
    result += get_number_with_sign_str(int(value[0]))
    result += get_number_with_sign_str(int(value[1]))
    return result

def send_serial(ser, value):
    ser.write(str.encode(value))
    logger.log_serial_send(value)


def handle_input(input_value):
    values = Joystick.get_deserialized_info(input_value)

    # TODO this might be optimized.
    with serial.Serial(COM_PORT, DATA_RATE_BPS) as ser:
        for value in values.axis:
            send_serial(ser, get_sendable_axis_value(value))
        for value in values.buttons:
            send_serial(ser, get_sendable_button_value(value))
        for value in values.hats:
            send_serial(ser, get_sendable_hat_value(value))


def read_data_from_peripherals():
    pass


def run():

    global logger

    # print('Enter the host name:')
    # hostname = input()

    logger_type = ''
    while logger_type not in ['none', 'printer']:
        print('Enter the logger type (none or printer):')
        logger_type = input()
    if logger_type == 'printer':
        logger = Logger(print)

    # parameters = {
    #     'hostname': hostname,
    #     'data_to_send_func': read_data_from_peripherals,
    #     'receiver_func': handle_input,
    #     'log_info': logger_type=='printer',
    #     'sender_logger': logger,
    #     'receiver_logger': logger,
    #     'wait_before_connecting': True
    # }

    # x = SenderReceiver(**parameters)
    # x.run()

    x = Server(handle_input, logger=logger)    
    x.accept_connections()


run()
