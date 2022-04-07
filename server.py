"""
Directly forward requests from a client.
Must be able to Port-forward

Author:
Nilusink
"""
from threading import Thread
import socket


PORTS_TO_CONNECT = [
    22,
]


def listen_for(port: int) -> None:
    """
    listen on a specific port and wait for one
    client to connect
    """
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(("0.0.0.0", port))
    serv.listen()

    while True:
        try:
            # wait until it got a valid connection
            # only accept one connection
            cl, addr = serv.accept()
            Client(cl, port)
            return

        except (Exception,):
            continue


class Client:
    """
    Connects to the computer that should be port-forwarded
    and forwards to other clients to connect
    """
    def __init__(self, socket_instance: socket, port: int) -> None:
        # "server client" setup
        self.__server = socket_instance

        # "client client" setup
        self.__client_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client_server.bind(("0.0.0.0", port))
        self.__client_server.listen()

        # general variables
        self.running = True
        self.__port = port

    @property
    def port(self) -> int:
        return self.__port

    def client_listener(self) -> None:
        """
        listens for a client to connect
        only accepts one client and waits for it to disconnect
        """
        while self.running:
            try:
                cl, addr = 1, 2

            except (Exception,):
                continue


def listen() -> None:
    """
    listen for servers connecting
    """
    for p in PORTS_TO_CONNECT:
        Thread(listen_for(p)).start()


def main() -> None:
    ...


if __name__ == "__main__":
    main()
