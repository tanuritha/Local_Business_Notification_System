import json
import logging
import socket
import time
from math import floor
from random import randint

from src.campus_event_notification_service.constants import constants as const


def initialize_socket(node_ip: str) -> socket:
    """
    Creates a socket and binds it to the given IP address and a random port.

    Args:
        node_ip (str): The IP address to bind the socket to.

    Returns:
        socket: The created socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (node_ip, 0)
    sock.bind(address)
    return sock


def find_index_by_identifier(id: int, nodes: list) -> int:
    """
    Finds the index of a server_node in a list by its ID.

    Args:
        id (int): The ID of the server_node to find.
        nodes (list): The list of nodes.

    Returns:
        int: The index of the server_node in the list, or 0 if the server_node is not found.
    """
    i = 0
    for j in nodes:
        if j.get("id") == id:
            return i
        i += 1
    return 0


def create_server_message(id: int, type: int, data: dict) -> bytes:
    """
    Creates a server message.

    Args:
        id (int): The ID of the server.
        type (int): The type of the message.
        data (dict): The data to include in the message.

    Returns:
        bytes: The created message as bytes.
    """
    data["type"] = type
    data["id"] = id
    msg = json.dumps(data)
    msg = str(msg).encode("utf-8")
    return msg


def build_message(
    node_id: int, type_of_msg: int, port_details: int, ip_value: str
) -> bytes:
    """
    Builds a message.

    Args:
        node_id (int): The ID of the server_node.
        type_of_msg (int): The type of the message.
        port_details (int): The port details to include in the message.
        ip_value (str): The IP value to include in the message.

    Returns:
        bytes: The built message as bytes.
    """
    msg = {"type": type_of_msg, "id": node_id, "port": port_details, "ip": ip_value}
    msg = json.dumps(msg)
    msg = str(msg).encode("utf-8")
    return msg


def find_identifier_by_port(port_value: int, li: list) -> int:
    """
    Finds the ID of a server_node in a list by its port value.

    Args:
        port_value (int): The port value of the server_node to find.
        li (list): The list of nodes.

    Returns:
        int: The ID of the server_node, or 0 if the server_node is not found.
    """
    for i in li:
        if i.get("port") == port_value:
            return i.get("id")
    return 0


def delay(is_needed: bool, upper_limit: int):
    """
    Delays execution if needed.

    Args:
        is_needed (bool): Whether a delay is needed.
        upper_limit (int): The upper limit for the delay in seconds.
    """
    if is_needed:
        time_delay = randint(0, floor(upper_limit * 1.5))
        time.sleep(time_delay)


def generate_identifier(list: list):
    identifier = randint(const.MIN, const.MAX)
    if identifier not in list:
        return identifier
    else:
        generate_identifier(list)


def configure_logging() -> logging:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(asctime)s\n%(message)s",
        datefmt="%b-%d-%y %I:%M:%S",
    )
    return logging
