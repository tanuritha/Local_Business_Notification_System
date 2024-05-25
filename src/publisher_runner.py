import argparse
import pyfiglet
import os
from modules.publisher import Publisher


def run_publisher():
    parser = argparse.ArgumentParser(
        description="Publisher Node"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        help="Increases output verbosity",
        action="store_true",
    )

    parser.add_argument(
        "-c",
        "--config_file",
        action="store",
        required=True,
        help="Requires JSON config file",
    )

    args = parser.parse_args()

    os.system("clear")
    intro = pyfiglet.figlet_format("PUBLISHER", font="doom")
    print(intro)

    publisher_node = Publisher(args.verbose, args.config_file)
    publisher_node.start_service()


if __name__ == "__main__":
    run_publisher()
