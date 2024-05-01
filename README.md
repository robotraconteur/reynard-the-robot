<p align="center"><img src="docs/figures/logo-header.svg"></p>

# Reynard the Robot

Reynard the Robot is a tool designed to help new users learn Robot Raconteur. It is designed to
provide a simple experience like the classic "Turtle" application, but with a robotics spin. Reynard is
a cartoon planar mobile robot with an attached articulated arm. He can be translated in X and Y in the plane,
and the arm has three revolute joints. For simplicity, Reynard cannot be rotated in the plane. In total,
Reynard has 5 degrees of freedom.

The application also has a simple chat window, where Reynard can send and receive messages to the user.

The color of the robot base can be changed. The default is an orange color, but the color can be changed to any
RGB value.

The software interface is designed to be representative of real devices, and provide a simple way
for users to begin using Robot Raconteur.

<p align="center"><img src="docs/figures/reynard_the_robot.png"></p>

The application is implemented as a simple Web application. A built in viewer based on PySide6 is used by
default to view the workspace, but the application can be used in "headless" mode and accessed by any
modern web browser.

Open a web browser to `http://localhost:29201` to view the workspace if running headless. Replace
`localhost` with the IP address of the computer running the application, and use the `--http-public` option.

By default, the Reynard Robot Raconteur service is available at `rr+tcp://localhost:29200/?service=reynard`.

Reynard is also designed to help users learn how to develop Robot Raconteur drivers. The application provides
the following software programming interfaces:

- Robot Raconteur
- Python Library API
- HTTP REST API
- Raw ASCII Socket
- ROS 1 (external package required)
- ROS 2 (external package required)

These interfaces are designed to be representative of real devices. Robot Raconteur drivers communicates with
the device using one of these (or similar) interfaces, and provides a Robot Raconteur service.

The ROS 1 and ROS 2 interfaces require external packages to operate. See 
https://github.com/johnwason/reynard_the_robot_ros and https://github.com/johnwason/reynard_the_robot_ros2

## Installation

### Installer for Windows

Reynard the Robot is available as an installer for Windows. See 
https://github.com/robotraconteur/reynard-the-robot/releases for the current release. Download the appropriate file,
and install as normal. These installers use the PySide6 based viewer. Shortcut icons are created
under the "Robot Raconteur" group on Windows. Windows may raise security warnings. If these are a problem,
use the `pip` method below.

If headless mode or other advanced
options are required, use the `pip` method.

### Mac OS

The pyside6 based viewer is not currently working on Mac OS. Use the `--headless` mode an open
a web browser to `http://localhost:29201`

```
python3 -m pip install --user reynard-the-robot
```

To run, use:

```
python3 -m reynard_the_robot --headless
```

Open a browser to http://localhost:29201

### Python Pip

`reynard-the-robot` requires Python 3.8 or higher. Install using:

```
python -m pip install --user reynard-the-robot[gui]
```

On Linux, use:

```
python3 -m pip install --user reynard-the-robot[gui]
```

If headless mode will be used, the `[gui]` option is not required:

```
python3 -m pip install --user reynard-the-robot
```

## Usage

### Installer Shortcuts

If the installer is used, simply use the shortcut icons to start Reynard the Robot.

### Command Line

```
reynard-the-robot [options]
```

Or use Python module invocation if the entrypoint does not work:

```
python3 -m reynard_the_robot [options]
```

Available options:

Here is the markdown documentation for the arguments:

- `--headless` - Run Reynard in headless mode (no GUI)
- `--disable-robotraconteur` - Disable Robot Raconteur service
- `--disable-ascii-socket` - Disable ASCII socket server
- `--http-public` - Use public IP for HTTP socket server. If omitted, only localhost connections are accepted
- `--http-port=` - Port for HTTP socket server. Default value is 29201
- `--ascii-socket-public` - Use public IP for ASCII socket server. If omitted, only localhost connections are accepted
- `--ascii-socket-port=` - Port for ASCII socket server. Default value is 29202
- `--quiet` - Suppress output

Standard Robot Raconteur command line options can also be used. See 
https://github.com/robotraconteur/robotraconteur/wiki/Command-Line-Options


## Client Usage

Multiple client interfaces are provided. See the following pages for more information on each interface:

- Robot Raconteur [docs/robotraconteur.md](docs/robotraconteur.md)
- Python API [docs/python_api.md](docs/python_api.md)
- HTTP REST API [docs/http_rest.md](docs/http_rest.md)
- Raw ASCII Socket [docs/socket.md](docs/socket.md)
- ROS 1 and ROS 2 [docs/ros.md](docs/ros.md)

Note that the ROS 1 and ROS 2 interfaces require external packages to operate. See [docs/ros.md](docs/ros.md) 
for more information.

## Client Examples

See the `examples/` directory for more examples.

```python
from RobotRaconteur.Client import *
import time
import numpy as np

# Connect to the Reynard service using a URL
c = RRN.ConnectService('rr+tcp://localhost:29200?service=reynard')

def new_message(msg):
    print(f"New message: {msg}")

# Connect a callback function to listen for new messages
c.new_message += new_message

# Read the current state using a wire "peek". Can also "connect" to receive streaming updates.
state, _ = c.state.PeekInValue()
print(state)

# Teleport the robot
c.teleport(0.1,-0.2)

# Drive the robot with no timeout
c.drive_robot(0.5,-0.2, -1, False)

# Wait for one second
time.sleep(1)

# Stop the robot
c.drive_robot(0, 0, -1, False)

# Set the arm position
c.setf_arm_position(np.deg2rad(100), np.deg2rad(-30), np.deg2rad(-70))

# Drive the arm using timeout and wait
c.drive_arm(np.deg2rad(10), np.deg2rad(-30), np.deg2rad(-15), 1.5, True)

# Set the color to red
c.color = (1, 0, 0)

# Read the color
print(f"Color: {c.color}")

time.sleep(1)

# Reset the color
c.color = (0.929, 0.49, 0.192)

# Say hello
c.say("Hello, World From Robot Raconteur!")
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.txt](LICENSE.txt) file for details.

The character "Reynard the Robot" is Copyright (C) 2024 John Wason, All Rights Reserved.

"Reynard the Robot" is developed by Wason Technology, LLC, New York, USA
