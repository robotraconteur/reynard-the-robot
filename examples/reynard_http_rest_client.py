import requests
import time

#  reynard-the-robot base urle
base_url = "http://localhost:29201/api"

# Read the current state
response = requests.get(base_url + "/state")
print(response.json())

# Teleport the robot
requests.post(base_url + "/teleport", json={"x": 100, "y": -200}).raise_for_status()

# Drive the robot
requests.post(base_url + "/drive_robot", json={"vel_x": 500, "vel_y": -200}).raise_for_status()

time.sleep(1)

# Stop the robot
requests.post(base_url + "/drive_robot", json={"vel_x": 0, "vel_y": 0}).raise_for_status()

# Set the arm position
requests.post(base_url + "/set_arm_position", json={"q1": 100, "q2": -30, "q3": -70}).raise_for_status()

# Drive the arm
requests.post(base_url + "/drive_arm", json={"q1": 10, "q2": -30, "q3": -15}).raise_for_status()

time.sleep(1)

# Stop the arm
requests.post(base_url + "/drive_arm", json={"q1": 0, "q2": 0, "q3": 0}).raise_for_status()

# Read the color
response = requests.get(base_url + "/color")
print(response.json())

# Set the color
requests.post(base_url + "/color", json={"r": 1, "g": 0, "b": 0}).raise_for_status()

# Say something
requests.post(base_url + "/say", json={"message": "Hello, World From HTTP!"}).raise_for_status()

# Read message queue
response = requests.get(base_url + "/messages")
print(response.json())


