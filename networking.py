import socket
import threading
from typing import Optional

SERVER_HOSTNAME = '0.0.0.0'
SERVER_PORT = 5050
HEADER_SIZE = 64  # in bits
DEFAULT_MESSAGE_LENGTH = 2048  # in bits
DISCONNECT_MESSAGE = '!DISCONNECT'


class Connection:
    def __init__(self, connection, address, port, encoding='UTF-8'):
        self.connection = connection
        self.address = address
        self.port = port
        self.encoding = encoding

    def receive(self, length):
        return self.connection.recv(length).decode(self.encoding)

    def sendWithoutEncoding(self, message):
        return self.connection.send(message, )

    def send(self, message):
        return self.sendWithoutEncoding(message.encode(self.encoding))

    def __str__(self):
        return f'{self.address}:{self.port}'


class Logger:

    @staticmethod
    def do_nothing():
        pass

    def __init__(self, log_func=print):
        self.log_func = log_func

    def log(self, msg):
        self.log_func(msg)

    def log_listening(self, addr):
        self.log(f'[LISTEN] listening on {addr}')

    def log_accept(self, addr):
        self.log(f'[ACCEPT] new connection from {addr}')

    def log_server_exit(self, addr):
        self.log(f'[EXIT] exiting server listening on {addr}')

    def log_receiver_exit(self, addr):
        self.log(f'[EXIT] exiting receiver connected to {addr}')

    def log_send(self, message, addr):
        self.log(f'[SEND] message: "{message}" to {addr}')

    def log_receive(self, message, addr):
        self.log(f'[RECEIVE] message: "{message}" from {addr}')

    def log_connecting(self, addr):
        self.log(f'[CONNECTING] address: {addr}')

    def log_connected(self, addr):
        self.log(f'[CONNECTED] address: {addr}')


class ReceiverCommon(threading.Thread):
    def __init__(self, connection, logger, receive_func):
        super().__init__()
        self.connection = connection
        self.logger = logger
        self.receive_func = receive_func

    def join(self, timeout: Optional[float] = ...) -> None:
        super().join(timeout)
        self.logger.log_receiver_exit(self.connection)

    def run(self) -> None:
        while True:
            message = self.receive()
            if message == DISCONNECT_MESSAGE:
                break
            self.receive_func(message)
            self.logger.log_receive(message, self.connection)


class VariableLengthReceiver(ReceiverCommon):
    def receive(self):
        message_length_str = self.connection.receive(HEADER_SIZE)
        if not message_length_str:
            return ''
        message_length = int(message_length_str)
        message = self.connection.receive(message_length)
        return message


class FixedLengthReceiver(ReceiverCommon):
    def __init__(self, connection, logger,
                 receive_func, message_length=DEFAULT_MESSAGE_LENGTH):
        super().__init__(connection, logger, receive_func)
        self.message_length = message_length

    def receive(self):
        message = self.connection.receive(self.message_length)
        return message


class SenderCommon:
    def __init__(self, logger):
        self.logger = logger

    def validate_message_length(self, current_length, desired_length):
        if desired_length < current_length:
            raise ValueError('Provided Message length is bigger than the desired length')

    def pad_encoded_message(self, message, desired_length):
        current_length = len(message)
        self.validate_message_length(current_length, desired_length)
        message += b' ' * (desired_length - current_length)
        return message


class VariableLengthSender(SenderCommon):
    def send(self, message, connection):
        message_length = len(message)
        message_length_str = str(message_length).encode(connection.encoding)
        message_length_str = self.pad_encoded_message(message_length_str, HEADER_SIZE)

        connection.sendWithoutEncoding(message_length_str)
        connection.send(message, )


class FixedLengthSender(SenderCommon):
    def __init__(self, logger, message_length=DEFAULT_MESSAGE_LENGTH):
        super().__init__(logger)
        self.message_length = message_length

    def send(self, message, connection):
        self.validate_message_length(len(message), self.message_length)
        connection.send(message, )


class SocketCommon:

    # TODO count for the case when a fixed length sender is used.
    def __init__(self, logger=Logger(), sender=VariableLengthSender):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger = logger
        self.sender = sender(self.logger)


class Server(SocketCommon):

    # TODO count for the case when a fixed length receiver is used.
    # TODO you might consider using a receiver factory.
    def __init__(self, receiver_func, logger=Logger(), receiver=VariableLengthReceiver):
        super().__init__(logger=logger)
        self.connections = []
        self.receivers = []
        self.receiver_func = receiver_func
        self.addr = (SERVER_HOSTNAME, SERVER_PORT)
        self.socket.bind(self.addr)
        self.receiver = receiver  # Storing just the class, not an instance

    def listen(self):
        self.logger.log_listening(self.addr)
        self.socket.listen()

    def startReceivingThread(self, connection):
        receiver = self.receiver(connection, self.logger, self.receiver_func)
        receiver.start()
        self.receivers.append(receiver)

    def acceptSocketConnection(self):
        (conn, (addr, port)) = self.socket.accept()
        connection = Connection(conn, addr, port)
        return connection

    def accept_connection(self):
        connection = self.acceptSocketConnection()
        self.connections.append(connection)
        self.logger.log_accept(connection)
        self.startReceivingThread(connection)

    def accept_connections(self):
        self.listen()
        while True:
            self.accept_connection()

    def send(self, message, connection):
        self.logger.log_send(message, connection)
        self.sender.send(message, connection)

    def exit(self):
        for receiver in self.receivers:
            receiver.join()
        self.logger.log_server_exit(self.addr)


class Client(SocketCommon):
    def __init__(self, hostname, port, logger=Logger(), sender=VariableLengthSender):
        super().__init__(sender=sender, logger=logger)
        address = (hostname, port)
        self.connection = Connection(self.socket, hostname, port)
        self.logger.log_connecting(self.connection)
        self.socket.connect(address)
        self.logger.log_connected(self.connection)

    def send(self, message):
        self.logger.log_send(message, self.connection)
        self.sender.send(message, self.connection)


class SenderReceiver:

    def get_logger(self, log_info, logger):
        if logger is None:
            logger = Logger(Logger.do_nothing if not log_info else print)

        return logger

    def start_receiver_thread(self):
        self.receiver = threading.Thread(target=self.server.accept_connections())
        self.receiver.run()

    def join_receiver_thread(self):
        self.receiver.join()


    def __init__(self, hostname, data_to_send_func, receiver_func, wait_before_connecting=False,
                 log_info=True, sender_logger=None, receiver_logger=None):
        self.get_data = data_to_send_func
        sender_logger = self.get_logger(log_info, sender_logger)
        receiver_logger = self.get_logger(log_info, receiver_logger)
        self.server = Server(receiver_func=receiver_func, logger=receiver_logger)
        self.start_receiver_thread()
        if wait_before_connecting:
            print('Server created successfuly, press enter to connect to the other server')
            input()
        self.client = Client(hostname=hostname, port=SERVER_PORT, logger=sender_logger)

    def run(self):
        while True:
            data = self.get_data()
            if not data:
                break
            self.client.send(data)
        self.join_receiver_thread()


def run_test_server():
    server = Server(print)
    server.accept_connections()


def get_test_client():
    client = Client(socket.gethostname(), SERVER_PORT)
    return client
