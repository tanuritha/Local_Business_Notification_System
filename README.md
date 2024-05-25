Local Business Notifications Pub Sub 
Description
This project is a Local Business Notification system based on the publish/subscribe architecture. It allows local businesses to publish promotions and subscribers to subscribe to categories of interest.

Setup
cd Local_Business_Notification_System

# create a venv
python -m venv venv

# activate venv
source venv/bin/activate

# Install the requirements
pip install -r requirements.txt


Local Execution
# Start register
$ python3 src/registration_runner.py -v -c src/configs/reg_config.json 

# start the server nodes in multiple terminals
$ python3 src/server_node_runner.py -v -c src/configs/node_config.json

# Start the subscriber
$ python3 src/subscription_runner.py -v -c src/configs/subscriber_config.json

# Start the publisher
$ python3 src/publisher_runner.py -v -c src/configs/publisher_config.json


Using EC2 instances
update the configs with the IP addresses of EC2 machines. Ensure EC2 instances are in the same VPC and inbound/outbound rules are updated to allow connection between the instances.

# SSh into the instance
ssh -i path_to_key_pair.pem_fle ec2-user@ip_instance
Run the setup again

# Start register
$ python src/registration_runner.py -v -c src/configs/reg_config.json 

# start the server nodes in multiple terminals
$ python src/server_node_runner.py -v -c src/configs/node_config.json

# Start the subscriber
$ python src/subscription_runner.py -v -c src/configs/subscriber_config.json

# Start the publisher
$ python src/publisher_runner.py -v -c src/configs/publisher_config.json

                                
  