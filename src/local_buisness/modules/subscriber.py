import json
import socket
import sys
from threading import Thread
import time

from src.local_buisness.constants.constants import Type


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
        self.interests = config["subscriber"].get("interests", [])
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
        Connects to the server. Sends a message to the leader about the port that the subscriber is listening to and the interests that it has.
        """
        msg = {
            "client_type": "subscriber",
            "ip": self.ip,
            "port": self.port,
            "interests": self.interests,
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
        finally:
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

            while True:
                conn, addr = subscriber_socket.accept()
                print(f"Connection established with {addr}, waiting for data...")
                # Using a loop to handle multiple messages
                while True:
                    data = conn.recv(BUFF_SIZE)
                    if not data:
                        print("No more data received. Closing connection.")
                        break  # Exit the inner loop if no data is received to wait for another connection.

                    msg = json.loads(data.decode("utf-8"))
                    print(f"\nData Received from the publisher: {msg}\n")
                    # Process based on interests

                    if "businessType" in msg and msg["businessType"] in self.interests:
                        print(f"New offer from {msg['businessType']}: {msg.get('offer', 'No offer details')}")
                    else:
                        print("Received message does not match subscribed interests or lacks 'businessType'.")

        except Exception as e:
            print(f"Exception occurred: {e}")
            sys.exit(1)
        finally:
            conn.close()
            subscriber_socket.close()

