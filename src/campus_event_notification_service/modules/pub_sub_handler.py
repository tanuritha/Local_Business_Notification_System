import json
import socket
from threading import Thread

from src.campus_event_notification_service.constants.constants import BUFF_SIZE, Type
from src.campus_event_notification_service.utils import utils as helper

school_subscribers_dict = {}


class PubSub:
    def __init__(self, leader, id, ip_leader, nodes, ip, port_leader):
        """
        Initializes a new instance of the PubSub class.

        Args:
            leader (int): The ID of the leader.
            id (int): The ID of this node.
            ip_leader (str): The IP address of the leader.
            nodes (list): The list of nodes.
            ip (str): The IP address of this node.
            port_leader (int): The port of the leader.
        """

        self.leader = leader
        self.id = id
        self.ip_leader = ip_leader
        self.nodes = nodes
        self.ip = ip
        self.port_leader = port_leader
        self.count_of_clients = 0

    def set_leader_id(self, leader):
        """
        Sets the ID of the leader.

        Args:
            leader (int): The new ID of the leader.
        """
        self.leader = leader

    def listen_to_client(self):
        """
        Listens for connections from clients. When a client connects, it receives data from the client,
        increments the client count, and determines which server should handle the client based on the client count.
        If this node is the leader and should handle the client, it calls process_client_data. Otherwise, it sends the client data
        to the server that should handle it.
        """

        accept_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        accept_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        accept_client_socket.settimeout(None)
        address = (self.ip_leader, self.port_leader)
        print("Leader is accepting publishers and subscribers\n")

        try:
            accept_client_socket.bind(address)
            accept_client_socket.listen()

            while True:
                conn, addr = accept_client_socket.accept()
                print("Connection Received from client...")

                data = eval(conn.recv(BUFF_SIZE).decode("utf-8"))
                print("Data received from client: ", data)

                self.count_of_clients += 1
                index = self.count_of_clients % len(self.nodes)

                print("Number of clients connected: ", self.count_of_clients)
                print(
                    "ID of the server that will handle the client: ",
                    self.nodes[index]["id"],
                )

                if self.nodes[index]["id"] == self.id:
                    print("Leader will handle the client\n")
                    self.process_client_data(data)
                else:
                    print("Sending the client data to the server...\n")
                    self.send_client_data_to_server(data, self.nodes[index])

                conn.close()
        except BaseException as e:
            print("")

        accept_client_socket.close()
        self.close_all_subscribers()

    def close_all_subscribers(self):
        """
        Closes all subscriber sockets.
        """
        for school, subscribers in school_subscribers_dict.items():
            for subscriber_socket in subscribers:
                subscriber_socket.close()

    def send_client_data_to_server(self, data, info):
        """
        Sends client data to a server.

        Args:
            data (dict): The client data to send.
            info (dict): Information about the server to send the data to.
        """
        temp_socket = helper.initialize_socket(self.ip)
        msg = helper.create_server_message(
            self.id, Type["CONNECT_TO_CLIENT"].value, data
        )

        client_handler_address = (info["ip"], info["port"])

        try:
            print(f"Sending client data to server {info}\n\n")
            temp_socket.connect(client_handler_address)
            temp_socket.send(msg)
            print("Data sent to server.")
            temp_socket.close()
        except BaseException as e:
            print("Error in sending data to server: ", e)
            temp_socket.close()

    def process_client_data(self, data):
        """
        Handles a client based on its type.

        Args:
            data (dict): The client data.
        """
        if data["client_type"] == "subscriber":
            print("This is a Subscriber\n")
            print("The schools of this subscriber are: ", data["school"])
            print("\n")
            self.process_subscriber(data)
        elif data["client_type"] == "publisher":
            print("This is a publisher\n")
            self.process_publisher(data)
        else:
            print("Unknown Client Type\n")

    def process_subscriber(self, data):
        """
        Processes a subscriber. Connects to the subscriber and adds it to the list of subscribers for each school it's interested in.

        Args:
            data (dict): The subscriber data.
        """
        print(f"Processing subscriber {data['ip']}:{data['port']}\n")
        for school in data["school"]:
            subscriber_address = (data["ip"], data["port"])
            subscriber_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            subscriber_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            subscriber_socket.settimeout(None)

            try:
                subscriber_socket.connect(subscriber_address)
                subscribers = school_subscribers_dict.get(school, set())
                subscribers.add(subscriber_socket)
                school_subscribers_dict[school] = subscribers
            except BaseException as e:
                print("Unable to connect to the subscriber", e)

        print(f"Subscriber list = {school_subscribers_dict}")

    def process_publisher(self, data):
        """
        Starts a new thread to listen to a publisher.

        Args:
            data (dict): The publisher data.
        """
        thread = Thread(target=self.listen_to_publisher, args=(data,))
        thread.daemon = True
        thread.start()

    def listen_to_publisher(self, publisher):
        """
        Listens to a publisher. When a message is received from the publisher, it is published to the relevant subscribers
        and broadcast to the other nodes.

        Args:
            publisher (dict): The publisher to listen to.
        """
        publisher_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        publisher_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        publisher_socket.settimeout(None)
        address = (publisher["ip"], publisher["port"])
        print(f"Publisher : {address} publishing data\n")

        try:
            publisher_socket.bind(address)
            publisher_socket.listen()

            conn, addr = publisher_socket.accept()
            print(f"Connection received: conn={conn}, addr={addr}\n")
            while True:
                data = eval(conn.recv(BUFF_SIZE).decode("utf-8"))
                print(f"Data received from publisher: {data}")

                self.publish_event_to_subscribers(data["school"], data["event"])
                self.broadcast(data)
        except BaseException as e:
            print("Error:", e)

        publisher_socket.close()

    def publish_event_to_subscribers(self, school, event):
        """
        Publishes a message to all subscribers of a school.

        Args:
            school (str): The school to publish the message to.
            event (str): The event to publish.
        """

        print("Sending the data to the subscribers\n")
        subscribers = school_subscribers_dict.get(school, set())
        print(f"Subscribers for school {school} = {subscribers}")

        msg = {"school": school, "event": event}
        for subscriber_socket in subscribers:
            print(f"Sending data to subscriber {subscriber_socket}\n")
            subscriber_socket.send(json.dumps(msg).encode("utf-8"))
            print("Data sent to subscriber.")

    def broadcast(self, data):
        """
        Broadcasts a message to all other nodes.

        Args:
            data (dict): The message to broadcast.
        """
        for info in self.nodes:
            if info["id"] == self.id:
                continue

            temp_socket = helper.initialize_socket(self.ip)
            msg = helper.create_server_message(
                self.id, Type["PUBLISH_DATA_TO_SUBSCRIBERS"].value, data
            )

            client_handler_address = (info["ip"], info["port"])

            try:
                print(f"Sending client data to server {info}\n\n")
                temp_socket.connect(client_handler_address)
                temp_socket.send(msg)
                temp_socket.close()
            except BaseException as e:
                print("Error in sending data to server: ", e)
                temp_socket.close()
