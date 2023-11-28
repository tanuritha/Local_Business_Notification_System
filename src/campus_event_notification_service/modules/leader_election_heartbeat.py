import logging
import os
import signal as sign
import socket
import sys
import time
from threading import Thread, Lock, Event

from src.campus_event_notification_service.constants.constants import (
    TOTAL_DELAY,
    BUFF_SIZE,
    DEFAULT_ID,
    HEARTBEAT_TIME,
    Type,
)
from src.campus_event_notification_service.utils import utils as helper
from .pub_sub_handler import PubSub


class BullyLeaderElection:
    def __init__(
        self,
        current_node_ip: str,
        current_node_port: int,
        id: int,
        nodes_topology_entities: list,
        socket: socket,
        log_data: bool,
        delay_time_interval: bool,
        is_bully_algorithm: bool,
        leader_node_ip: str,
        leader_node_port: int,
    ):
        """
        Initializes a new instance of the Bully_leader_election class.

        Args:
            current_node_ip (str): The IP address of the current node.
            current_node_port (int): The port of the current node.
            id (int): The ID of the current node.
            nodes_topology_entities (list): The list of nodes in the network.
            socket (socket): The socket for the current node.
            log_data (bool): Whether to log data.
            delay_time_interval (bool): Whether to delay time intervals.
            is_bully_algorithm (bool): Whether the bully algorithm is used.
            leader_node_ip (str): The IP address of the leader node.
            leader_node_port (int): The port of the leader node.
        """

        self.checkedNodesLength = 0

        self.coordinatorMessageFlag = False

        self.nodeIP = current_node_ip
        self.nodePort = current_node_port
        self.nodeId = id
        self.nodes = nodes_topology_entities
        self.socket = socket
        self.algo = is_bully_algorithm
        self.leaderIP = leader_node_ip
        self.leaderPort = leader_node_port

        self.leaderID = DEFAULT_ID
        self.coordinatorport = DEFAULT_ID
        self.lock = Lock()

        self.delay = delay_time_interval
        self.verbose = log_data
        self.is_leader_elected = Event()

        sign.signal(sign.SIGINT, self.handler)

        self.logging = self.log_data()

        self.algoFlag = False

        self.pub_sub = PubSub(
            self.leaderID,
            self.nodeId,
            self.leaderIP,
            self.nodes,
            self.nodeIP,
            self.leaderPort,
        )

        thread = Thread(target=self.monitor_connections)
        thread.daemon = True
        thread.start()

        self.initiate_election()
        print("Waiting until the leader is elected...")
        self.is_leader_elected.wait()
        print("Leader is elected. The id of the leader is: ", self.leaderID)
        print("Starting heartbeat...")
        HeartBeat(
            self.nodeIP,
            self.nodePort,
            self.nodeId,
            self.nodes,
            self.socket,
            self.verbose,
            self.delay,
            self.algo,
            self.leaderIP,
            self.leaderPort,
            self.leaderID,
            self.lock,
            self.algoFlag,
        )

    def initiate_election(self):
        """
        Initiates a leader election. If this node has the highest ID among the nodes that are still up, it becomes the leader.
        Then, it sends an END message to all other nodes to inform them that the election is over and it is the new leader.
        Finally, it starts a new thread to listen to clients.
        """
        print("Starting leader election...")
        self.lock.acquire()
        current_position = helper.find_index_by_identifier(self.nodeId, self.nodes) + 1
        print("Current position is: ", current_position)
        print("The nodes in the list are: ", self.nodes)
        self.algoFlag = True
        self.coordinatorMessageFlag = False

        if (current_position != len(self.nodes)) and (
            self.low_id_node(current_position) == 0
        ):
            return

        self.leaderID = self.nodeId
        self.algoFlag = False

        print(
            "Leader is elected and the details are : ",
            {"ip": self.nodeIP, "port": self.nodePort, "id": self.nodeId},
        )

        close = False
        for node in range(len(self.nodes) - 1):
            sock = helper.initialize_socket(self.nodeIP)
            if node == (current_position - 1):
                continue
            try:
                sock.connect((self.nodes[node]["ip"], self.nodes[node]["port"]))
                close = True
                self.forward_message(self.nodes[node], self.nodeId, Type["END"], sock)
                sock.close()
            except ConnectionRefusedError:
                sock.close()
                continue

        if not close:
            self.socket.close()
            os._exit(1)

        self.pub_sub.set_leader_id(self.leaderID)

        client_thread = Thread(target=self.pub_sub.listen_to_client)
        client_thread.daemon = True
        client_thread.start()

        self.lock.release()

    def forward_message(
        self, node: dict, nodeId: int, message_type: Type, conn: socket
    ):
        """
        Forwards a message to a node.

        Args:
            :param message_type: The type of the message.
            :param node:  The node to forward the message to.
            :param conn: The socket to use to send the message.
            :param nodeId: The ID of the node that is forwarding the message.
        """

        helper.delay(self.delay, TOTAL_DELAY)
        dest = (node["ip"], node["port"])
        msg = helper.build_message(
            nodeId, message_type.value, self.nodePort, self.nodeIP
        )
        try:
            conn.send(msg)
        except ConnectionResetError:
            return

    def wait_for_longer(self):
        """
        Waits for a certain amount of time (TOTAL_DELAY) for a coordinator message. If a coordinator message is received during this time,
        it sets the algorithm flag and the coordinator message flag to False and returns 0. If no coordinator message is received,
        it sets the algorithm flag to False and returns 1.
        """
        timeout_value = time.time() + TOTAL_DELAY
        while time.time() < timeout_value:
            self.lock.acquire()
            if self.coordinatorMessageFlag == True:
                self.algoFlag = False
                self.coordinatorMessageFlag = False
                self.lock.release()
                return 0
            self.lock.release()

        self.lock.acquire()
        self.algoFlag = False
        return 1

    def message_answered(self):
        """
        Decreases the number of checked nodes by 1.
        """
        self.lock.acquire()
        self.checkedNodesLength -= 1
        self.lock.release()

    def process_end_message(self, msg: dict):
        """
        Processes an END message. Sets the coordinator port, leader ID, leader IP, leader port, and coordinator message flag based on the message.

        Args:
            msg (dict): The END message.
        """
        self.lock.acquire()
        self.coordinatorport = msg["port"]
        self.leaderID = msg["id"]
        self.leaderIP = msg["ip"]
        self.leaderPort = msg["port"]
        self.is_leader_elected.set()
        self.coordinatorMessageFlag = True
        self.lock.release()

    def process_election_message(self, msg: dict):
        """
        Processes an ELECTION message. Sends an ANSWER message to the sender of the ELECTION message. If the algorithm flag is False,
        it initiates a new election.

        Args:
            msg (dict): The ELECTION message.
        """

        self.lock.acquire()
        sock = helper.initialize_socket(self.nodeIP)
        try:
            print((msg["ip"], msg["port"]))
            sock.connect((msg["ip"], msg["port"]))
            self.forward_message(msg, self.nodeId, Type["ANSWER"], sock)
        except ConnectionRefusedError:
            pass

        sock.close()

        if self.algoFlag == False:
            self.lock.release()
            self.initiate_election()
            return

        self.lock.release()

    def low_id_node(self, index: int) -> int:
        """
        Checks if there are any nodes with a lower ID that are still up. If there are, it sends an ELECTION message to each of them.
        Then, it waits for a certain amount of time for an ANSWER message from each of them. If it receives an ANSWER message from all of them,
        it returns 0. If it doesn't receive an ANSWER message from at least one of them, it returns 1.

        Args:
            index (int): The current position in the list of nodes.

        Returns:
            int: 0 if an ANSWER message is received from all nodes with a lower ID, 1 otherwise.
        """

        self.leaderID = DEFAULT_ID
        self.checkedNodesLength = len(self.nodes) - index
        ack_nodes = self.checkedNodesLength
        exit = False
        for node in range(index, len(self.nodes)):
            sock = helper.initialize_socket(self.nodeIP)
            try:
                sock.connect((self.nodes[node]["ip"], self.nodes[node]["port"]))
                self.forward_message(
                    self.nodes[node], self.nodeId, Type["ELECTION"], sock
                )
                sock.close()
                exit = True
            except ConnectionRefusedError:
                sock.close()
                continue

        if exit == False:
            return 1
        self.lock.release()
        timeout_interval = time.time() + TOTAL_DELAY
        while time.time() < timeout_interval:
            self.lock.acquire()
            if self.checkedNodesLength != ack_nodes:
                self.lock.release()
                if self.wait_for_longer() == 0:
                    return 0
                else:
                    return 1
            self.lock.release()

        self.lock.acquire()
        return 1

    def monitor_connections(self):
        """
        Monitors connections to the node. If a connection is received, it starts a new thread to handle the connection.
        """
        while True:
            self.lock.acquire()

            self.socket.settimeout(None)
            self.lock.release()

            try:
                connection, addr = self.socket.accept()
            except socket.timeout:
                self.logging.debug(
                    "[Node]: (ip:{} port:{} id:{})\n[Terminates]\n".format(
                        self.nodeIP, self.nodePort, self.nodeId
                    )
                )
                self.socket.close()
                os._exit(1)

            data = connection.recv(BUFF_SIZE)

            if not data:
                continue

            data = eval(data.decode("utf-8"))

            if self.leaderID == self.nodeId and data["type"] == Type["HEARTBEAT"].value:
                print("Received heartbeat from node: ", data["id"])
                helper.delay(self.delay, TOTAL_DELAY)

                msg = helper.build_message(
                    self.nodeId, Type["ACK"].value, self.nodePort, self.nodeIP
                )
                print("Sending ack to node: ", data["id"])
                connection.send(msg)
                connection.close()
                continue

            elif data["type"] == Type["ANSWER"].value:
                self.message_answered()
                connection.close()
                continue

            elif data["type"] == Type["CONNECT_TO_CLIENT"].value:
                print(f"Data received from client: {data}")
                connection.close()

                self.pub_sub.process_client_data(data)
                continue

            elif data["type"] == Type["PUBLISH_DATA_TO_SUBSCRIBERS"].value:
                print(f"Data received from Publisher: {data}")
                connection.close()

                self.pub_sub.publish_event_to_subscribers(data["school"], data["event"])
                continue

            elif data["type"] == Type["SUBSCRIBE"].value:
                if data["school"] == "PING":
                    data = {"response": "ACK"}
                    str(data).encode("utf-8")
                    print(data)
                    connection.send(str(data).encode("utf-8"))
                else:
                    print(data, "\n\n")
                    str(data).encode("utf-8")
                    print(data)
                    msg = helper.build_message(
                        self.nodeId, Type["SUBSCRIBE"].value, self.nodePort, self.nodeIP
                    )

                    connection.send(str(data).encode("utf-8"))
                connection.close()
                continue

            func = {
                Type["ELECTION"].value: self.process_election_message,
                Type["END"].value: self.process_end_message,
            }

            if data["type"] in func:
                func[data["type"]](data)
            else:
                print(f"Unknown type: {data['type']}")
            connection.close()

    def handler(self, signum: int, frame):
        """
        Handles a SIGINT signal. Shuts down the node and logs the shutdown.

        Args:
            signum (int): The signal number.
            frame (frame): The current stack frame.
        """

        self.logging.debug(
            "[Node]: (ip:{} port:{} id:{})\n[Killed]\n".format(
                self.nodeIP, self.nodePort, self.nodeId
            )
        )
        self.socket.close()
        sys.exit(1)

    def log_data(self) -> logging:
        """
        Sets up logging for the node. Returns a logging object.
        """
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)s] %(asctime)s\n%(message)s",
            datefmt="%b-%d-%y %I:%M:%S",
        )

        return logging


class HeartBeat:
    def __init__(
        self,
        nodeIP: str,
        nodePort: int,
        nodeId: int,
        nodes: list,
        socket: socket,
        log_data: bool,
        delay_time_interval: bool,
        is_bully_algorithm: bool,
        leader_node_ip: str,
        leader_node_port: int,
        leader_id: int,
        lock: Lock,
        algoFlag: bool,
    ):
        self.nodeIP = nodeIP
        self.nodePort = nodePort
        self.nodeId = nodeId
        self.nodes = nodes
        self.socket = socket
        self.verbose = log_data
        self.delay = delay_time_interval
        self.algo = is_bully_algorithm
        self.leaderIP = leader_node_ip
        self.leaderPort = leader_node_port
        self.leaderID = leader_id
        self.lock = lock
        self.algoFlag = algoFlag

        self.start_heartbeat()

    def start_heartbeat(self):
        """
        Creates a hearbeat socket and starts sending heartbeat to the leader node. 
        If the leader node is not available, handle_crash is called.
        
        """
        while True:
            heratbeat_socket = helper.initialize_socket(self.nodeIP)
            address = heratbeat_socket.getsockname()

            time.sleep(HEARTBEAT_TIME)
            self.lock.acquire()

            if self.algoFlag or (self.leaderID in [self.nodeId, DEFAULT_ID]):
                self.lock.release()
                continue

            index = helper.find_index_by_identifier(self.leaderID, self.nodes)
            info = self.nodes[index]

            print("Creating heartbeat message...")

            msg = helper.build_message(
                self.nodeId, Type["HEARTBEAT"].value, address[1], address[0]
            )

            dest = (info["ip"], info["port"])

            print("Heartbeat message is created")
            try:
                heratbeat_socket.connect(dest)
                print(f"sending heartbeat to the leader node with id: {info['id']}")
                heratbeat_socket.send(msg)
                self.receive_acknowledgement(
                    heratbeat_socket,
                    dest,
                    TOTAL_DELAY,
                    self.algo,
                    self.nodes,
                    self.lock,
                    self.leaderID,
                )
                print(f"received ack from the Leader\n\n")

            except ConnectionRefusedError:
                heratbeat_socket.close()
                self.handle_crash(self.algo, self.lock)

    def receive_acknowledgement(self, sock, dest, waiting, algo, nodes, lock, leaderID):
        """
        Processes the hearbeat acknowledgement received from leader. 
        If the acknowledgement is not received within the waiting time,
        handle_crash is called.
        """
        start = round(time.time())
        sock.settimeout(waiting)

        try:
            data = sock.recv(BUFF_SIZE)
        except (socket.timeout, ConnectionResetError):
            sock.close()
            self.handle_crash(algo, lock)
            return

        if not data:
            sock.close()
            self.handle_crash(algo, lock)
            return

        msg = eval(data.decode("utf-8"))

        if (msg["id"] == leaderID) and (msg["type"] == Type["ACK"].value):
            lock.release()

        else:
            stop = round(time.time())
            waiting -= stop - start
            self.receive_acknowledgement(
                sock, dest, waiting, algo, self.nodes, lock, leaderID
            )

        addr = (msg["ip"], msg["port"])
        sock.close()

    def handle_crash(self, algo, lock):
        """
        Handles the crash of the leader node. Initiates a new election.

        """
        self.nodes.pop()
        lock.release()
        BullyLeaderElection(
            self.nodeIP,
            self.nodePort,
            self.nodeId,
            self.nodes,
            self.socket,
            self.verbose,
            self.delay,
            self.algo,
            self.leaderIP,
            self.leaderPort,
        )
