from networking import SenderReceiver, Logger, do_nothing, Server, SERVER_PORT
from joystick import Joystick
from time import sleep

try:
    import serial
except ModuleNotFoundError:
    import pip

    pip.main(['install', 'pyserial'])
finally:
    import serial

# TODO just for now. later, try to list
#  the ports and choose according to some logic.
current_com_port_index = 0
COM_PORTS = ['/dev/ttyACM0', '/dev/ttyACM1']
DATA_RATE_BPS = 9600

AXIS_MULTIPLIER = 1000
AXIS_DIGITS_COUNT = 4

DEFAULT_LOGGER_STR = 'printer'

END_OF_MESSAGE = '\n'

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


def send_serial(ser, message):
    message = str.encode(message)
    ser.write(message)
    logger.log_serial_send(message)


def handle_input(input_value):

    try:
        values = Joystick.get_deserialized_info(input_value)
    except Exception:
        print('Error happened when trying to deserialize the input value.')
        print('Input value: ' + str(input_value))
        print('Returning...')
        return

    global current_com_port_index

    # TODO this might be optimized.
    while True:
        try:
            with serial.Serial(COM_PORTS[current_com_port_index], DATA_RATE_BPS) as ser:
                message = ''
                for value in values.axis:
                    message += get_sendable_axis_value(value)
                for value in values.buttons:
                    message += get_sendable_button_value(value)
                for value in values.hats:
                    message += get_sendable_hat_value(value)
                message += END_OF_MESSAGE
                send_serial(ser, message)
                break
        except Exception:
            print('Error happened while sending to ' + COM_PORTS[current_com_port_index] + '.')
            current_com_port_index += 1
            current_com_port_index %= len(COM_PORTS)
            print('Switching to ' + COM_PORTS[current_com_port_index] + '...')
            sleep(1)


def read_data_from_peripherals():
    pass


def run():
    global logger

    # print('Enter the host name:')
    # hostname = input()

    logger_type = ''
    while logger_type not in ['none', 'printer']:
        print(f'Enter the logger type (none or printer) [Default = {DEFAULT_LOGGER_STR}]:')
        logger_type = input() or DEFAULT_LOGGER_STR
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

    while True:
        try:
            x = Server(handle_input, logger=logger)
            x.accept_connections()
        except Exception:
            print('Error happened while starting the server. Retrying in 1 second...')
            sleep(1)


run()
