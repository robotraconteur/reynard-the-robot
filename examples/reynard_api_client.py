from reynard_the_robot import Reynard
import time

# Callback function for new_message signal


def new_message(_, message):
    print(message + " in callback")


# Create a Reynard object
reynard = Reynard()

# Start the Reynard object
reynard.start()

# Connect the new_message signal to the new_message callback function
reynard.new_message.connect(new_message)

# Read the robot position and arm position
print(f"Robot position: {reynard.robot_position}")
print(f"Arm position: {reynard.arm_position}")

# Teleport the robot
reynard.teleport(100, -200)

# Drive the robot
reynard.drive_robot(500, -200)

# Wait for 1 second
time.sleep(1)

# Stop the robot
reynard.drive_robot(0, 0)

# Set the arm position
reynard.set_arm_position(100, -30, -70)

# Drive the arm
reynard.drive_arm(10, -30, -15)

# Wait for 1 second
time.sleep(1)

# Stop the arm
reynard.drive_arm(0, 0, 0)


# Set the color to Red
reynard.color = (1, 0, 0)

# Read the color
print(f"Color: {reynard.color}")

time.sleep(1)

# Set the color to Green
reynard.color = (0, 1, 0)

time.sleep(1)

# Reset the color
reynard.color = (0.929, 0.49, 0.192)

# Say hello
reynard.say("Hello, World From API!")
