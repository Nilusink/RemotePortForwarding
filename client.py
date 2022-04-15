"""
run on the device you want to port-forward

Author:
Nilusink
"""
from threading import Thread
import typing as tp
import socket
import signal
import sys


RUNNING: bool = True
SERVER_ADDRESS: tp.Tuple[str, int] = ("127.0.0.1", 2222)
LOCAL_PORT: int = 3333


class Client:
    """
    Connects to the computer that should be port-forwarded
    and forwards to other clients to connect
    """
    def __init__(self, server_address: tp.Tuple[str, int], local_port: int) -> None:
        # "server client" setup
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.connect(server_address)

        # client setup
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect(("127.0.0.1", local_port))

        # general variables
        self.running = True
        self.__port = local_port

        # starting threads
        Thread(target=self.server_receiver).start()
        Thread(target=self.client_receiver).start()

    @property
    def port(self) -> int:
        return self.__port

    def client_receiver(self) -> None:
        """
        receives messages from a client
        connected trough client_listener
        """
        print(f"Message thread up")
        while self.running:
            try:
                # receive message and forward it to the actual server
                msg = self.__client.recv(4096)
                if msg:
                    print(f"goint out: {msg}")
                else:
                    print(f"outgoing spam", end="\r")
                self.__server.send(msg)

            except TimeoutError:
                continue

            except (Exception,):
                self.__client.close()
                self.__client: socket.socket = ...
                return

    def server_receiver(self) -> None:
        """
        receives messages from the server
        and forwards them to the client
        """
        buffer: list = []
        self.__server.settimeout(.1)
        while self.running:
            try:
                msg = self.__server.recv(4096)
                if msg:
                    print(f"coming in: {msg}")
                else:
                    print(f"incomming spam", end="\r")
                if self.__client is ...:
                    buffer.append(msg)
                    continue
                self.__client.send(msg)

            except TimeoutError:
                if self.__client is not ... and buffer:
                    for msg in buffer:
                        self.__client.send(msg)

                continue

            except (Exception,):
                if self.__client is not ...:
                    self.__client.close()
                    self.__client = ...
                continue


def main() -> int:
    """
    main function
    """
    to_catch = [
        signal.SIGINT,
        signal.SIGTERM
    ]
    # handle exit signals
    for s in to_catch:
        signal.signal(s, terminate)

    # create client instance
    Client(SERVER_ADDRESS, LOCAL_PORT)

    return 0


def terminate(*signals) -> None:
    """
    properly close the program
    """
    global RUNNING
    RUNNING = False
    sys.exit(signals[0])


if __name__ == "__main__":
    terminate(main())
