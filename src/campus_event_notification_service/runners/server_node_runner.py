import argparse
import pyfiglet
import os

from src.campus_event_notification_service.modules.server_node import ServerNode


def run_server_node():
    algorithm_options = argparse.ArgumentParser(
        description="Implementation of distributed election algorithms.\nGeneric server_node."
    )

    algorithm_options.add_argument(
        "-v",
        "--verbose",
        default=False,
        help="increase output verbosity",
        action="store_true",
    )
    algorithm_options.add_argument(
        "-d",
        "--delay",
        default=False,
        help="generate a random delay to forwarding messages",
        action="store_true",
    )
    algorithm_options.add_argument(
        "-c",
        "--config_file",
        action="store",
        help="needed a config file in json format",
    )

    args = algorithm_options.parse_args()

    if not (args.config_file):
        algorithm_options.error("JSON FILE NOT PROVIDED")

    os.system("clear")
    intro = pyfiglet.figlet_format("NODE", font="slant")
    print(intro)
    print("This is a server_node of the distributed system")

    node = ServerNode(args.verbose, True, args.config_file, args.delay)
    node.start_server()


if __name__ == "__main__":
    run_server_node()
