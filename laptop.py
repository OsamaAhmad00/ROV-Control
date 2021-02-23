from networking import SenderReceiver, Client, SERVER_PORT
from joystick import Joystick
import pygame


MESSAGES_PER_SECOND = 30


def handle_input(value):
    pass


def run():
    print('Enter the host name of the server:')
    hostname = input()
    joystick = Joystick()

    # parameters = {
    #     'hostname': hostname,
    #     'data_to_send_func': joystick.get_serialized_info,
    #     'receiver_func': handle_input
    # }
      
    # x = SenderReceiver(**parameters)
    # x.run()

    x = Client(hostname=hostname, port=SERVER_PORT)
    clock = pygame.time.Clock()
    while True:
        clock.tick(MESSAGES_PER_SECOND)
        x.send(joystick.get_serialized_info())


run()
