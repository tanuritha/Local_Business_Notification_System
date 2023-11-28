import argparse
import pyfiglet
import os
from src.campus_event_notification_service.modules.publisher import Publisher


def run_publisher():
    parser = argparse.ArgumentParser(
        description="Implementation of distributed election algorithms.\nGeneric server_node."
    )

    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        help="increase output verbosity",
        action="store_true",
    )

    parser.add_argument(
        "-c",
        "--config_file",
        action="store",
        required=True,
        help="needed a config file in json format",
    )

    args = parser.parse_args()

    os.system("clear")
    intro = pyfiglet.figlet_format("PUBLISHER", font="slant")
    print(intro)

    publisher_node = Publisher(args.verbose, args.config_file)
    publisher_node.start_service()


if __name__ == "__main__":
    run_publisher()
