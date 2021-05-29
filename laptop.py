from networking import SenderReceiver, Client, SERVER_PORT
from joystick import Joystick
from time import sleep
import pygame
from cv_adjust import CVAdjust

DEFAULT_MESSAGES_PER_SECOND = 8
DEFAULT_SERVER_HOSTNAME = "192.168.1.111"
DEFAULT_CAMERA_ID = 0
CV_ADJUST_1_SKIP_WORD = 'x'
MINIMUM_CV_ADJUST_1_TOGGLE_PERIOD_SECONDS = 2


def handle_input(value):
    pass


def get_joystick():
    while True:
        try:
            joystick = Joystick()
            break
        except Exception:
            print('Error happened while recognizing the joystick. Retrying in 1 second...')
            Joystick.reinit()
            sleep(1)
    return joystick


# def get_cv_adjust():
#     while True:
#         try:
#             cv_adjust = CVAdjust()
#             break
#         except Exception:
#             print('Error happened while recognizing the camera. Retrying in 1 second...')
#             sleep(1)
#     return cv_adjust


class JoystickController:
    class UniqueMessageGetter:
        def __init__(self):
            self.last_str = ''

        def get_next_str(self, new_str):
            if new_str == self.last_str:
                return None
            self.last_str = new_str
            return new_str

    CV_ADJUST1_DISABLE_ENABLE_BUTTON_INDEX = 5

    def joystick_getter(self):
        self.joystick_str = self.joystick.get_serialized_info()
        result = self.joystick_result.get_next_str(self.joystick_str)
        self.joystick_str_is_new = result is not None
        return result

    def cv_adjust1_getter(self):
        if self.cv_adjust1 is None:
            return None
        try:
            result = self.cv_adjust1.process_and_get_value()
            return self.cv_adjust1_result.get_next_str(result)
        except Exception:
            print('There was an error reading values from the camera.')
            return None

    def __init__(self, client, joystick, cv_adjust1=None):
        self.client = client
        self.joystick_str = ''
        self.joystick_str_is_new = False
        self.joystick = joystick
        self.joystick_result = self.UniqueMessageGetter()
        self.cv_adjust1 = cv_adjust1
        self.cv_adjust1_result = self.UniqueMessageGetter()
        self.getters = [('Joystick', self.joystick_getter,), ('Camera', self.cv_adjust1_getter,)]

    def initialize_cv_adjust_1(self):
        while True:
            print('Enter the id of the camera (usually 0 for webcam, 1 for the additional camera) or '
                  f'"{CV_ADJUST_1_SKIP_WORD}" to skip or enter for the default id ({DEFAULT_CAMERA_ID}): ')
            id_str = input() or str(DEFAULT_CAMERA_ID) # may be done better?
            if id_str.lower() == CV_ADJUST_1_SKIP_WORD.lower():
                return
            try:
                camera_id = int(id_str)
            except Exception:
                print('Please enter a valid number.')
                continue

            try:
                self.cv_adjust1 = CVAdjust(camera_id)
                return
            except Exception:
                print('The entered id is not valid try again.')

    def enable_or_disable_cv_adjust_1(self):

        toggle_char = '0'

        if self.joystick_str != '':
            values = Joystick.get_deserialized_info(self.joystick_str)
            if self.CV_ADJUST1_DISABLE_ENABLE_BUTTON_INDEX < len(values.buttons):
                toggle_char = values.buttons[self.CV_ADJUST1_DISABLE_ENABLE_BUTTON_INDEX]
            else:
                print('Button ' + str(self.CV_ADJUST1_DISABLE_ENABLE_BUTTON_INDEX) + '( used for toggling the '
                                                                                     'camera doesn\'t exits in '
                                                                                     'this joystick.')

        if toggle_char == '1' and self.joystick_str_is_new:
            if self.cv_adjust1 is None:
                self.initialize_cv_adjust_1()
            else:
                self.cv_adjust1 = None

    def get_and_send(self):
        for getter in self.getters:
            result = getter[1]()
            if result is not None:
                self.client.send(result, getter[0])
        self.enable_or_disable_cv_adjust_1()


def run():
    print(f'Enter the host name of the server [Default = {DEFAULT_SERVER_HOSTNAME}]:')
    hostname = input() or DEFAULT_SERVER_HOSTNAME

    print(f'Enter the number of messages per second [Default = {str(DEFAULT_MESSAGES_PER_SECOND)}]:')
    mps = int(input() or DEFAULT_MESSAGES_PER_SECOND)

    joystick = get_joystick()
    # cv_adjust = CVAdjust()

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
                    client = Client(hostname=hostname, port=SERVER_PORT)
                    break
                except Exception:
                    print('Error happened while connecting to the server. Retrying in 1 second...')
                    sleep(1)

            controller = JoystickController(client=client, joystick=joystick)

            clock = pygame.time.Clock()
            while True:
                clock.tick(mps)
                controller.get_and_send()

        except Exception:
            # TODO end the client.
            print('Error happened while sending the info. Possibly the server has disconnected.')
            print('Trying to connect again...')
            sleep(1)


run()
