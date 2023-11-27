from setuptools import setup, find_packages

setup(
    name="CampusEventNotificationService",
    version="1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "start_registration=src.campus_event_notification_service.runners.registration_runner:run_registration",
            "start_publisher=src.campus_event_notification_service.runners.publisher_runner:run_publisher",
            "start_server_nodes=src.campus_event_notification_service.runners.server_node_runner:run_server_node",
            "start_subscriber=src.campus_event_notification_service.runners.subscription_runner:run_subscriber",

        ],
    },
    test_suite="tests",
)
