"""
Directly forward requests from a client.
Must be able to Port-forward

Author:
Nilusink
"""
from threading import Thread
import typing as tp
import socket
import signal
import sys


# first argument of the tuple is the initial port,
# the second argument is the actual port to connect to
PORTS_TO_CONNECT = [
    (2222, 22222)
]
RUNNING: bool = True


def listen_for(port: tp.Tuple[int, int]) -> None:
    """
    listen on a specific port and wait for one
    client to connect
    """
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(("0.0.0.0", port[0]))
    serv.listen()

    print(f"listening on {port[0]}")
    serv.settimeout(.1)
    while RUNNING:
        try:
            # wait until it got a valid connection
            # only accept one connection
            cl, addr = serv.accept()
            Client(cl, port[1])
            return

        except TimeoutError:
            continue

        except (Exception,):
            continue


class ClientPool:
    instance: "ClientPool" = ...

    def __new__(cls, *args, **kwargs) -> "ClientPool":
        """
        checks if there is already an instance of the ClientPool
        and returns that if it exists, so it is globally synced
        """
        if cls.instance is not ...:
            return cls.instance

        cls.instance = super(ClientPool, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        """
        Collector for all Client classes intended for better management
        """
        self.__clients: tp.List[Client] = []

    def append(self, client: "Client") -> None:
        """
        add a client to the pool
        """
        self.__clients.append(client)

    def stop_all(self) -> None:
        """
        close all connections and stop the clients
        """
        for client in self.__clients:
            client.running = False


class Client:
    """
    Connects to the computer that should be port-forwarded
    and forwards to other clients to connect
    """
    def __init__(self, socket_instance: socket.socket, port: int) -> None:
        # "server client" setup
        self.__server = socket_instance

        # "client client" setup
        self.__client_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client_server.bind(("0.0.0.0", port))
        self.__client_server.listen()

        self.__client_client: socket.socket = ...
        self.__client_client_ready_connect: bool = False

        # general variables
        self.running = True
        self.__port = port

        # starting threads
        Thread(target=self.client_listener).start()
        Thread(target=self.server_receiver).start()

        # appending itself to the ClientPool class
        ClientPool().append(self)

        print(f"Started client, listening on {port}")

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
                cl, addr = self.__client_server.accept()
                print(f"received client: {addr}")
                if self.__client_client is not ...:
                    cl.close()
                    continue

                self.__client_client = cl
                self.__client_client_ready_connect = True
                Thread(target=self.client_receiver).start()
                print(f"started receiving messages")

            except (Exception,):
                continue

    def client_receiver(self) -> None:
        """
        receives messages from a client
        connected trough client_listener
        """
        if self.__client_client is ... or not self.__client_client_ready_connect:
            return

        self.__client_client_ready_connect = False
        print(f"Message thread up")
        while self.running:
            try:
                # receive message and forward it to the actual server
                print(f"waiting for message")
                msg = self.__client_client.recv(2048)
                print(f"got message: {msg}")
                self.__server.send(msg)

            except TimeoutError:
                continue

            except (Exception,):
                self.__client_client.close()
                self.__client_client: socket.socket = ...
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
                msg = self.__server.recv(2048)
                if self.__client_client is ...:
                    buffer.append(msg)
                    continue
                self.__client_client.send(msg)

            except TimeoutError:
                if self.__client_client is not ... and buffer:
                    for msg in buffer:
                        self.__client_client.send(msg)

                continue

            except (Exception,):
                if self.__client_client is not ...:
                    self.__client_client.close()
                    self.__client_client = ...
                continue


def listen() -> None:
    """
    listen for servers connecting
    """
    for p in PORTS_TO_CONNECT:
        Thread(target=listen_for, args=[p]).start()


def main() -> None:
    to_catch = [
        signal.SIGINT,
        signal.SIGTERM
    ]
    # handle exit signals
    for s in to_catch:
        signal.signal(s, terminate)

    listen()
    input("Press Enter to stop")


def terminate(*signals) -> None:
    """
    properly close the program
    """
    global RUNNING
    RUNNING = False
    ClientPool().stop_all()
    sys.exit(signals[0])


if __name__ == "__main__":
    main()
