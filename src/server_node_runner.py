import argparse
import pyfiglet
import os

from modules.server_node import ServerNode


def run_server_node():
    algorithm_options = argparse.ArgumentParser(
        description="Server_node."
    )

    algorithm_options.add_argument(
        "-v",
        "--verbose",
        default=False,
        help="Increases output verbosity",
        action="store_true",
    )
    algorithm_options.add_argument(
        "-d",
        "--delay",
        default=False,
        help="Adds a random delay amount for the forwarding messages",
        action="store_true",
    )
    algorithm_options.add_argument(
        "-c",
        "--config_file",
        action="store",
        help="Requires a JSON config file",
    )

    args = algorithm_options.parse_args()

    if not (args.config_file):
        algorithm_options.error("JSON FILE NOT PROVIDED")

    os.system("clear")
    intro = pyfiglet.figlet_format("NODE", font="doom")
    print(intro)
    print("This is a server_node")

    node = ServerNode(args.verbose, True, args.config_file, args.delay)
    node.start_server()


if __name__ == "__main__":
    run_server_node()
