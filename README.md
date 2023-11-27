# Campus Event Notification Service

## Description

This project is a Campus Event Notification Service based on the publish/subscribe architecture. It allows publishers to publish events and subscribers to subscribe to events of interest. The service is designed to efficiently distribute event notifications to a large number of subscribers in a campus setting.

### Setup

```bash
# create a venv
python -m venv venv
# activate venv
source venv/bin/activate
# Install the requirements
pip install -r requirements.txt
```

### Local Execution

```bash
# Start register
$ cd CENS/register
$ python3 server_node_runner.py -v -c reg_config.json

# start the server nodes in multiple terminals
$ cd CENS/server_node/
$ python3 server_node_runner.py -v -c node_config.json

# Start the subscriber
$ cd CENS/subscriber/
$ python3 server_node_runner.py -v -c subscriber_config.json

# Start the publisher
$ cd CENS/publisher/
$ python3 server_node_runner.py -v -c publisher_config.json                                   

```

### Using EC2 instances

```bash
# SSh into the instance
ssh -i path_to_key_pair.pem_fle ec2-user@ip_instance

# Start the register
cd distributedSystem/register/
python3 server_node_runner.py -v -c ../local_config.json

# Start the server nodes
cd distributedSystem/server_node/
python3 server_node_runner.py -v -c ../local_config.json

# Start the subscriber
$ cd distributedSystem/subscriber/
$ python3 server_node_runner.py -v -c ../local_config_subscriber.json

# Start the publisher
$ cd distributedSystem/publisher/
$ python3 server_node_runner.py -v -c ../local_config_publisher.json  
```
