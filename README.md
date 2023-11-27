# Campus Event Notification Service

## Description

This project is a Campus Event Notification Service based on the publish/subscribe architecture. It allows publishers to publish events and subscribers to subscribe to events of interest. The service is designed to efficiently distribute event notifications to a large number of subscribers in a campus setting.

### Setup

```bash
cd CENS

# create a venv
python -m venv venv

# activate venv
source venv/bin/activate

# Install the requirements
pip install -r requirements.txt

# build the CENS service
python -m build

# Install the service
pip install dist/CampusEventNotificationService-1.0-py3-none-any.whl
```

### Local Execution

```bash
# Start register
$ start_registration -v -c src/campus_event_notification_service/configs/reg_config.json 

# start the server nodes in multiple terminals
$ start_server_nodes -v -c src/campus_event_notification_service/configs/node_config.json

# Start the subscriber
$ start_subscriber -v -c src/campus_event_notification_service/configs/subscriber_config.json

# Start the publisher
$ start_publisher -v -c src/campus_event_notification_service/configs/publisher_config.json                                

```

### Using EC2 instances

update the configs with the IP addresses of EC2 machines. Ensure EC2 instances are in the same VPC and inbound/outbound rules are updated to allow connection between the instances.

```bash
# SSh into the instance
ssh -i path_to_key_pair.pem_fle ec2-user@ip_instance
```
Run the setup again

```bash
# Start register
$ start_registration -v -c src/campus_event_notification_service/configs/reg_config.json 

# start the server nodes in multiple terminals
$ start_server_nodes -v -c src/campus_event_notification_service/configs/node_config.json

# Start the subscriber
$ start_subscriber -v -c src/campus_event_notification_service/configs/subscriber_config.json

# Start the publisher
$ start_publisher -v -c src/campus_event_notification_service/configs/publisher_config.json                                
  
```
