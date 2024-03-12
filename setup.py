from setuptools import setup, find_packages

setup(
    name="LocalBuisnessNotificationService",
    version="1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "start_registration=src.local_buisness.runners.registration_runner:run_registration",
            "start_publisher=src.local_buisness.runners.publisher_runner:run_publisher",
            "start_server_node=src.local_buisness.runners.server_node_runner:run_server_node",
            "start_subscriber=src.local_buisness.runners.subscription_runner:run_subscriber",
        ],
    },
    test_suite="tests",
)
