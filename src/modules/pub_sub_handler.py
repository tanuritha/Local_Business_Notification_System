import json
import socket
from threading import Thread

from constants.constants import BUFF_SIZE, Type
from utils import utils as helper

business_subscribers_dict = {}

class PubSub:
    def __init__(self, leader, id, ip_leader, nodes, ip, port_leader):
        self.leader = leader
        self.id = id
        self.ip_leader = ip_leader
        self.nodes = nodes
        self.ip = ip
        self.port_leader = port_leader
        self.count_of_clients = 0

    def set_leader_id(self, leader):
        self.leader = leader

    def listen_to_client(self):
        accept_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        accept_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        accept_client_socket.settimeout(None)
        address = (self.ip_leader, self.port_leader)
        print("Leader node is accepting clients(publishers and subscribers)\n")

        try:
            accept_client_socket.bind(address)
            accept_client_socket.listen()
            while True:
                conn, addr = accept_client_socket.accept()
                print("Received Connection from client")
                data = eval(conn.recv(BUFF_SIZE).decode("utf-8"))
                print("Received Data from client: ", data)
                self.process_client_data(data)
                conn.close()
        except BaseException as e:
            print(f"Exception occurred: {e}")
        finally:
            accept_client_socket.close()
            self.close_all_subscribers()

    def close_all_subscribers(self):
        for _, subscribers in business_subscribers_dict.items():
            for subscriber_info in subscribers:
                # Assuming subscriber_info is a dict with 'ip' and 'port'
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.connect((subscriber_info['ip'], subscriber_info['port']))
                        sock.close()
                except Exception as e:
                    print(f"Error closing connection to subscriber {subscriber_info}: {e}")

    def process_client_data(self, data):
        if data["client_type"] == "subscriber":
            print("This is a Subscriber\n")
            self.process_subscriber(data)
        elif data["client_type"] == "publisher":
            print("This is a Publisher\n")
            self.process_publisher(data)
        else:
            print("Unknown Client Type\n")

    def process_subscriber(self, data):
        print(f"Processing subscriber {data['ip']}:{data['port']}\n")
        interests = data.get('interests', [])
        subscriber_info = {'ip': data['ip'], 'port': data['port']}
        for interest in interests:
            if interest not in business_subscribers_dict:
                business_subscribers_dict[interest] = []
            business_subscribers_dict[interest].append(subscriber_info)
        print(f"Updated subscriber list: {business_subscribers_dict}")

    def process_publisher(self, data):
        thread = Thread(target=self.listen_to_publisher, args=(data,))
        thread.daemon = True
        thread.start()

    def listen_to_publisher(self, publisher):
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
                self.publish_event_to_subscribers(data["businessType"], data.get("offer", ""))
                self.broadcast(data)
        except BaseException as e:
            print("Error:", e)
        finally:
            publisher_socket.close()

    def publish_event_to_subscribers(self, businessType, offer):
        print("Sending the data to the subscribers\n")
        subscribers = business_subscribers_dict.get(businessType, [])
        msg = {"businessType": businessType, "offer": offer}
        for subscriber_info in subscribers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((subscriber_info['ip'], subscriber_info['port']))
                    sock.sendall(json.dumps(msg).encode("utf-8"))
                    print(f"Data sent to subscriber at {subscriber_info}")
            except Exception as e:
                print(f"Error sending data to subscriber {subscriber_info}: {e}")

    def broadcast(self, data):
        for info in self.nodes:
            if info["id"] == self.id:
                continue
            temp_socket = helper.initialize_socket(self.ip)
            msg = helper.create_server_message(self.id, Type["PUBLISH_DATA_TO_SUBSCRIBERS"].value, data)
            client_handler_address = (info["ip"], info["port"])
            try:
                temp_socket.connect(client_handler_address)
                temp_socket.send(msg)
                print(f"Broadcasted data to server {info}\n")
            except BaseException as e:
                print(f"Error broadcasting data to server {info}: {e}")
            finally:
                temp_socket.close()
