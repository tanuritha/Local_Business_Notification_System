import argparse
import pyfiglet
import os
from modules.subscriber import Subscriber


def run_subscriber():
    parser = argparse.ArgumentParser(
        description="Subscriber Node"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        help="Increase output verbosity",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--config_file",
        action="store",
        required=True,
        help="Requires a JSON config file",
    )

    args = parser.parse_args()

    os.system("clear")
    intro = pyfiglet.figlet_format("SUBSCRIBER", font="doom")
    print(intro)

    subscriber_node = Subscriber(args.verbose, args.config_file)
    subscriber_node.start_service()


if __name__ == "__main__":
    run_subscriber()
