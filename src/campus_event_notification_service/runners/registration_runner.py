import argparse
import os
import pyfiglet

from src.campus_event_notification_service.modules.registration import Register


def run_registration():
    parser = argparse.ArgumentParser(
        description="Implementation of distributed election algorithms.\nRegister server_node."
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
    intro = pyfiglet.figlet_format("REGISTER SERVICE", font="slant")
    print(intro)
    print("This service is responsible for assigning ID to the servers\n")

    register = Register(args.verbose, args.config_file)
    register.receive_connection_request()
    register.send_details()


if __name__ == "__main__":
    run_registration()
