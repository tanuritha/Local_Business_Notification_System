import json
import logging
import sys

from src.campus_event_notification_service.constants.constants import (
    BUFF_SIZE,
    DEFAULT_ID,
)
from src.campus_event_notification_service.utils import utils as helper
from .bully_leader_election import BullyLeaderElection, Type


class ServerNode:
    def __init__(
        self,
        log_data: bool,
        is_bully: bool,
        configuration_path_value: str,
        delay_time_interval: bool,
    ):
        with open(configuration_path_value, "r") as configuration_file:
            configValues = json.load(configuration_file)

        self.algorithm = is_bully
        self.registerPort = configValues["register"]["port"]
        self.registerIP = configValues["register"]["ip"]
        self.delay = delay_time_interval
        self.leaderIP = configValues["leader"]["ip"]
        self.leaderPort = configValues["leader"]["port"]
        self.nodeIP = configValues["node"]["ip"]
        self.verbose = log_data

    def start_server(self):
        socket_registry_service = helper.initialize_socket(self.nodeIP)

        sock_temp = helper.initialize_socket(self.nodeIP)
        sock_temp.listen()

        # socket used in listening phase
        sock = helper.initialize_socket(self.nodeIP)
        sock.listen()

        logging = logData()

        msg = helper.build_message(
            DEFAULT_ID,
            Type["REGISTER"].value,
            sock.getsockname()[1],
            sock.getsockname()[0],
        )
        destnation = (self.registerIP, self.registerPort)

        try:
            print("Trying to connect to register service")
            socket_registry_service.connect(destnation)
        except ConnectionRefusedError:
            print("Register node not available")
            sock.close()
            sys.exit(1)

        print("Connected to register service, sending message to register service")
        socket_registry_service.send(msg)

        data = socket_registry_service.recv(BUFF_SIZE)

        print("Received data from register service")
        if not data:
            sock.close()
            print("No data is received from register service")
            sys.exit(1)

        data = eval(data.decode("utf-8"))
        identifier = helper.find_identifier_by_port(sock.getsockname()[1], data)

        print("The ID assigned to this node is : ", identifier)
        print("The list of nodes received from register service is : ", data)
        socket_registry_service.close()

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
                self.leaderIP,
                self.leaderPort,
            )


def logData() -> logging:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(asctime)s\n%(message)s",
        datefmt="%b-%d-%y %I:%M:%S",
    )

    return logging
