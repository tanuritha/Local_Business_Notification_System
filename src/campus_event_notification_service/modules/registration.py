import json
import signal
import socket
import sys

from src.campus_event_notification_service.constants import constants as const
from src.campus_event_notification_service.utils import utils as helper


class Register:
    def __init__(self, verbose: bool, config_path: str):
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

    def receiveConnectionRequest(self):
        self.sock.listen()
        print("Register is listening on port {}".format(self.my_port))
        ids = []
        self.sock.settimeout(const.SOCKET_TIMEOUT)
        while True:
            try:
                conn, addr = self.sock.accept()
                data = conn.recv(const.BUFF_SIZE)
                msg = eval(data.decode("utf-8"))
                server_ip = {"ip": addr[0]}
                print(
                    "A server is trying to register with the following ip : ", server_ip
                )
                if msg["type"] != const.REGISTER:
                    conn.close()
                    continue

                identifier = helper.generate_identifier(ids)
                self.connections.append(conn)
                node = dict({"ip": addr[0], "port": msg["port"], "id": identifier})
                self.nodes.append(node)

                print(
                    "An ID is assigned to the server and the details are :",
                    {"ip": addr[0], "port": msg["port"], "id": identifier},
                )
                print("\n")

            except socket.timeout:
                break

        self.nodes.sort(key=lambda x: x["id"])
        if self.nodes:
            print("Register received the following servers and their details are:\n")
            print(self.nodes)
        else:
            print("Register did not receive any server\n")

    def sendDetails(self):
        data = str(self.nodes).encode("utf-8")
        for node in range(len(self.nodes)):
            print("Sending the details of the servers to the servers....")
            port = self.nodes[node]["port"]
            try:
                self.connections[node].send(data)
            except socket.timeout:
                print("Error: no ack from server_node on port {}".format(port))

        self.close()

    def handler_log_msgs(self, signum: int, frame):
        self.logging.debug(
            "[Register]: (ip:{} port:{})\n[Killed]\n".format(self.my_ip, self.my_port)
        )
        self.close()

    def close(self):
        self.sock.close()
        sys.exit(1)
