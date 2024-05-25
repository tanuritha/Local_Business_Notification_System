import argparse
import os
import pyfiglet
from modules import registration


def run_registration():
    parser = argparse.ArgumentParser(
        description="Register Node"
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
        type=str,
        action="store",
        required=True,
        help="Requires JSON config file",
    )

    args = parser.parse_args()

    os.system("clear")
    intro = pyfiglet.figlet_format("REGISTER", font="doom")
    print(intro)
    print("The register node assigns IDs to the servers\n")

    register = registration.Register(args.verbose, args.config_file)
    register.receive_connection_request()
    register.send_details()


if __name__ == "__main__":
    run_registration()
