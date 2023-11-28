import json
import logging
import sys

from src.campus_event_notification_service.constants.constants import (
    BUFF_SIZE,
    DEFAULT_ID,
)
from src.campus_event_notification_service.utils import utils as helper
from .leader_election_heartbeat import BullyLeaderElection, Type


class ServerNode:
    def __init__(
        self,
        log_data: bool,
        is_bully: bool,
        configuration_path_value: str,
        delay_time_interval: bool,
    ):
        """
        Initialize the ServerNode class.

        Args:
            log_data (bool): A flag used for enabling verbose logging.
            is_bully (bool): A flag used to determine if the node is a bully.
            configuration_path_value (str): The path to the configuration file.
            delay_time_interval (bool): A flag used to determine if there should be a delay in the time interval.
        """

        # Load configuration values from the provided file
        with open(configuration_path_value, "r") as configuration_file:
            configValues = json.load(configuration_file)

        # Initialize class attributes based on the configuration values and provided arguments
        self.algorithm = is_bully
        self.register_port = configValues["register"]["port"]
        self.register_ip = configValues["register"]["ip"]
        self.delay = delay_time_interval
        self.leader_ip = configValues["leader"]["ip"]
        self.leader_port = configValues["leader"]["port"]
        self.nodeIP = configValues["node"]["ip"]
        self.verbose = log_data

    def start_server(self):
        
        """
        Start the server.

        This method initializes the server, sets up the necessary sockets, and starts listening for connections.
        It also handles the registration of the server with the register service.
        """

        # Initialize socket for registry service
        register_socket = helper.initialize_socket(self.nodeIP)

        sock_temp = helper.initialize_socket(self.nodeIP)
        sock_temp.listen()

        # Initialize temporary socket and set it to listen
        sock = helper.initialize_socket(self.nodeIP)
        sock.listen()

        logging = helper.configure_logging()

        msg = helper.build_message(
            DEFAULT_ID,
            Type["REGISTER"].value,
            sock.getsockname()[1],
            sock.getsockname()[0],
        )
        destnation = (self.register_ip, self.register_port)

        try:
            print("Trying to connect to register service")
            register_socket.connect(destnation)
        except ConnectionRefusedError:
            print("Register node not available")
            sock.close()
            sys.exit(1)

        # Send registration message to the registry service
        print("Connected to register service, sending message to register service")
        register_socket.send(msg)

        data = register_socket.recv(BUFF_SIZE)

        print("Received data from register service")
        if not data:
            sock.close()
            print("No data is received from register service")
            sys.exit(1)

        data = eval(data.decode("utf-8"))
        identifier = helper.find_identifier_by_port(sock.getsockname()[1], data)

        print("The ID assigned to this node is : ", identifier)
        print("The list of nodes received from register service is : ", data)
        register_socket.close()

        # Check if there are enough nodes
        if len(data) == 1:
            sock.close()
            print("Not enough nodes generated!")
            sys.exit(1)

        if self.algorithm:
            BullyLeaderElection(
                sock.getsockname()[0],
                sock.getsockname()[1],
                identifier,
                data,
                sock,
                self.verbose,
                self.delay,
                self.algorithm,
                self.leader_ip,
                self.leader_port,
            )
