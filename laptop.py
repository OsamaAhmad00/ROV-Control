from networking import SenderReceiver
from joystick import Joystick


def handle_input(value):
    pass


def run():
    print('Enter the host name of the server:')
    hostname = input()
    joystick = Joystick()

    parameters = {
        'hostname': hostname,
        'data_to_send_func': joystick.get_serialized_info,
        'receiver_func': handle_input
    }

    x = SenderReceiver(**parameters)
    x.run()


run()
