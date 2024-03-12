import json
import socket
import time

from src.local_buisness.constants.constants import Type

class Publisher:
    def __init__(self, verbose: bool, config_path: str):
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.leaderPort = config["leader"]["port"]
        self.leaderIP = config["leader"]["ip"]
        self.pubIP = config["publisher"]["ip"]
        self.pubPort = config["publisher"]["port"]
        self.verbose = verbose

    def start_service(self):
        msg = {"client_type": "publisher", "ip": self.pubIP, "port": self.pubPort}

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.settimeout(None)
        address = (self.leaderIP, self.leaderPort)

        try:
            server_socket.connect(address)
            print("Connected to Leader Node, Sending message to Leader server_node")
            server_socket.send(json.dumps(msg).encode("utf-8"))
            server_socket.close()

            self.publish_data()
        except BaseException as e:
            print("Server server_node not available", e)



    def publish_data(self):
            
        time.sleep(2)

        publisher_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        publisher_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        publisher_socket.settimeout(None)
        address = (self.pubIP, self.pubPort)

        try:
            publisher_socket.connect(address)
            while True:
                print("Enter the business details: ")


            # Prompt for user input
                print("Enter the business details: ")
                business_type = input("Enter the Business Type: ")
                offer = input("Enter the offer details: ")

                user_input = {
                "businessType": business_type,
                "offer": offer
            }
                encoded_data = str(user_input).encode("utf-8")
                publisher_socket.send(encoded_data)
                print(f"{encoded_data} Data sent to the server!")

        except BaseException as e:
            print("Publisher server_node not available", e)