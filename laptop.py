from networking import SenderReceiver, Client, SERVER_PORT
from joystick import Joystick
from time import sleep
import pygame

DEFAULT_MESSAGES_PER_SECOND = 100
DEFAULT_SERVER_HOSTNAME = "192.168.1.111"


def handle_input(value):
    pass


def get_joystick():
    while True:
        try:
            joystick = Joystick()
            break
        except Exception:
            print('Error happened while recognizing the joystick. Retrying in 1 second...')
            sleep(1)
    return joystick


def run():
    print(f'Enter the host name of the server [Default = {DEFAULT_SERVER_HOSTNAME}]:')
    hostname = input() or DEFAULT_SERVER_HOSTNAME

    print(f'Enter the number of messages per second [Default = {str(DEFAULT_MESSAGES_PER_SECOND)}]:')
    mps = int(input() or DEFAULT_MESSAGES_PER_SECOND)

    joystick = get_joystick()

    # parameters = {
    #     'hostname': hostname,
    #     'data_to_send_func': joystick.get_serialized_info,
    #     'receiver_func': handle_input
    # }

    # x = SenderReceiver(**parameters)
    # x.run()

    while True:
        try:
            while True:
                try:
                    x = Client(hostname=hostname, port=SERVER_PORT)
                    break
                except Exception:
                    print('Error happened while connecting to the server. Retrying in 1 second...')
                    sleep(1)

            clock = pygame.time.Clock()
            prev_str = ''
            cur_str = ''
            while True:
                clock.tick(mps)
                cur_str = joystick.get_serialized_info()
                if cur_str != prev_str:
                    x.send(cur_str)
                    prev_str = cur_str

        except Exception:
            print('Error happened while sending the info. Possibly the server has disconnected.')
            print('Trying to connect again...')
            sleep(1)


run()
