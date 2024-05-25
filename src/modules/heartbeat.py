import socket
import time
from utils import utils
from threading import Thread, Lock, Event
from constants.constants import (
    TOTAL_DELAY,
    BUFF_SIZE,
    DEFAULT_ID,
    HEARTBEAT_TIME,
    Type,
)

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
            heratbeat_socket = utils.initialize_socket(self.nodeIP)
            address = heratbeat_socket.getsockname()

            time.sleep(HEARTBEAT_TIME)
            self.lock.acquire()

            if self.algoFlag or (self.leaderID in [self.nodeId, DEFAULT_ID]):
                self.lock.release()
                continue

            index = utils.find_index_by_identifier(self.leaderID, self.nodes)
            info = self.nodes[index]

            print("Creating heartbeat message")

            msg = utils.build_message(
                self.nodeId, Type["HEARTBEAT"].value, address[1], address[0]
            )

            dest = (info["ip"], info["port"])

            print("Heartbeat message creation complete")
            try:
                heratbeat_socket.connect(dest)
                print(f"Sending heartbeat to the leader node with id: {info['id']}")
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
                print(f"Received ACK from Leader node\n\n")

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

