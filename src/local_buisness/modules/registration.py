import json
import signal
import socket
import sys

from src.local_buisness.constants import constants as const
from src.local_buisness.utils import utils as helper


class Register:
    def __init__(self, verbose: bool, config_path: str):
        """
        Initialize the Register class.

        Args:
            verbose (bool): A flag used for enabling verbose logging.
            config_path (str): The path to the configuration file.
        """
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.my_ip = config["register"]["ip"]
        self.my_port = config["register"]["port"]

        self.nodes = []
        self.verbose = verbose
        self.logging = helper.configure_logging()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.my_ip, self.my_port))
        self.connections = []

        signal.signal(signal.SIGINT, self.handler_log_msgs)

    def receive_connection_request(self):
        """
        Listen for incoming connection requests and handle them.

        This method starts a server that listens for incoming connection requests.
        When a request is received, it generates an identifier for the new connection,
        stores the connection details, and prints the details.
        """
        self.sock.listen()
        print("Register is listening on port {}".format(self.my_port))
        ids = []
        self.sock.settimeout(const.SOCKET_TIMEOUT)
        while True:
            try:
                conn, addr = self.sock.accept()
                data = conn.recv(const.BUFF_SIZE)
                msg = json.loads(data.decode("utf-8"))

                print(f"A server is trying to register from {addr}")

                if 'type' not in msg or msg['type'] != const.REGISTER:
                    print("Invalid registration request received.")
                    conn.close()
                    continue

                # Handling new fields: node type and interests/business categories if applicable
                node_type = msg.get("node_type", "generic")  # Default to 'generic' if not specified
                interests = msg.get("interests", [])  # Specific for subscribers

                identifier = helper.generate_identifier([node['id'] for node in self.nodes])
                self.connections.append(conn)
                node = {
                    "ip": addr[0],
                    "port": msg["port"],
                    "id": identifier,
                    "type": node_type,  # Store the node type
                    "interests": interests  # Store interests if any
                }
                self.nodes.append(node)

                print(f"Assigned ID {identifier} to the server with details: {node}")

            except socket.timeout:
                break

        self.nodes.sort(key=lambda x: x["id"])
        if self.nodes:
            print("Register received the following servers and their details are:\n")
            print(self.nodes)
        else:
            print("Register did not receive any server\n")

    def send_details(self):
        """
        Send the details of the registered servers to each server.

        This method encodes the server details into a byte string and sends it to each server.
        If a server does not acknowledge the receipt of the details within a timeout period,
        an error message is printed.
        """
        data = str(self.nodes).encode("utf-8")
        for node in range(len(self.nodes)):
            print("Sending the details of the servers to the servers....")
            port = self.nodes[node]["port"]
            try:
                self.connections[node].send(data)
            except socket.timeout:
                print("Error: no ack from server_node on port {}".format(port))

        self.sock.close()
        sys.exit(1)

    def handler_log_msgs(self, signum: int, frame):
        """
        Handle log messages.

        This method is triggered when a signal is received. It logs a message indicating
        that the Register was killed, along with the Register's IP and port.

        Args:
            signum (int): The signal number.
            frame: The current stack frame.
        """
        self.logging.debug(
            "[Register]: (ip:{} port:{})\n[Killed]\n".format(self.my_ip, self.my_port)
        )
        self.sock.close()
        sys.exit(1)
        
