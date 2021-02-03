from networking import SenderReceiver
from joystick import Joystick


def handle_input(value):
    pass


def run():
    hostname = input()
    port = int(input())
    joystick = Joystick()

    parameters = {
        'hostname': hostname,
        'port': port,
        'data_to_send_func': joystick.get_serialized_info,
        'receiver_func': handle_input
    }

    x = SenderReceiver(**parameters)
    x.run()


run()
