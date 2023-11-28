import json
import socket
import sys
from threading import Thread

BUFF_SIZE = 1024


class Subscriber:
    def __init__(self, verbose: bool, config_path: str):
        """
        Initializes a new instance of the Subscriber class.

        Args:
            verbose (bool): Whether to print verbose output.
            config_path (str): The path to the configuration file.
        """

        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.port_leader = config["leader"]["port"]
        self.ip_leader = config["leader"]["ip"]
        self.ip = config["subscriber"]["ip"]
        self.port = config["subscriber"]["port"]
        self.school = config["subscriber"]["school"]
        self.verbose = verbose

    def start_service(self):
        """
        Starts the subscriber service. Starts a new thread to connect to the server, then listens to its own port.
        """

        thread = Thread(target=self.connect_with_server)
        thread.daemon = True
        thread.start()

        self.listen_to_port()

    def connect_with_server(self):
        """
        Connects to the server. Sends a message to the leader about the port that the subscriber is listening to and the topics that it is interested in.
        """

        msg = {
            "client_type": "subscriber",
            "ip": self.ip,
            "port": self.port,
            "school": self.school,
        }

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.settimeout(None)
        address = (self.ip_leader, self.port_leader)

        try:
            server_socket.connect(address)
            print("Sending the connection request to the leader...")
            server_socket.send(json.dumps(msg).encode("utf-8"))
            print("Connection request sent to the leader")
        except BaseException as e:
            print("Unable to connect to Leader", e)

        server_socket.close()

    def listen_to_port(self):
        """
        Listens to the subscriber's own port.
        """
        subscriber_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        subscriber_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        address = (self.ip, self.port)
        print("Creating subscriber socket.")
        try:
            subscriber_socket.bind(address)
            subscriber_socket.listen(5)
            print("This subscriber is listening to address: ", address)
            

            conn, addr = subscriber_socket.accept()
            print("waiting for data...")
            while True:
                data = conn.recv(BUFF_SIZE)
                if data != "":
                    msg = json.loads(data.decode("utf-8"))
                    print(f"\nData Received from the publisher.\n")
                    print(
                        "The school",
                        msg["school"],
                        " has announced the following event: ",
                        msg["event"],
                    )

        except BaseException as e:
            print("Exception:", e)
            sys.exit(1)
