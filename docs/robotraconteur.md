# Service: `experimental.reynard_the_robot`

The `experimental.reynard_the_robot` service provides types to interact with the Reynard the Robot cartoon robot.

Note that the Robot Raconteur service uses meters and radians as the units for all positions and velocities. This
is different from other interfaces which uses millimeters and degrees. Robot Raconteur services are expected to use
MKS SI units.

## Struct `ReynardState`

The `ReynardState` struct contains the current state of Reynard.

- `field double time`

   The current time in seconds. The time is the number of seconds since the Reynard server was started.

- `field double[] robot_position`

   The current position of the robot body in meters. The position is given as a 2 element array `[x, y]`.

- `field double[] arm_position`

   The current position of the robot arm joints in radians. The position is given as a 3 element array `[q1, q2, q3]`.

- `field double[] robot_velocity`

   The current velocity of the robot body in meters per second. The velocity is given as a 2 element array `[vel_x, vel_y]`.

- `field double[] arm_velocity`

    The current velocity of the robot arm joints in radians per second. The velocity is given as a 3
    element array `[vel_q1, vel_q2, vel_q3]`.

## Object `Reynard`

The `Reynard` object provides members to interact with Reynard.

### Properties

- `property double[] robot_position [readonly]`

   The current position of the robot body in meters. The position is given as a 2 element array `[x, y]`.

- `property double[] color`

   The current color of Reynard as an RGB array `[r, g, b]`. The color is given as a 3 element array with each element
   in the range 0 to 1.

### Functions

- `function void teleport(double x, double y)`

    Instantaneously move the robot body to the specified position in meters.
    - `x`: The x position in meters
    - `y`: The y position in meters

- `function double[] getf_arm_position()`

    Get the robot arm joints to the specified position in radians.

    - Returns: The arm joint angles as a 3 element array `[q1, q2, q3]` in radians.

- `function void drive_robot(double vel_x, double vel_y, double timeout, bool wait)`

    Drive the robot body at the specified velocity in meters per second.
    - `vel_x`: The x velocity in meters per second
    - `vel_y`: The y velocity in meters per second
    - `timeout`: The timeout in seconds. If the timeout is reached, the robot will stop. Set to -1 to drive indefinitely.
    - `wait`: If true, the function will block until the timeout is reached.

- `function void drive_arm(double q1, double q2, double q3, double timeout, bool wait)`

    Drive the robot arm joints to the specified position in radians.
    - `q1`: The position of joint 1 in radians per second
    - `q2`: The position of joint 2 in radians per second
    - `q3`: The position of joint 3 in radians per second
    - `timeout`: The timeout in seconds. If the timeout is reached, the robot will stop. Set to -1 to drive indefinitely.
    - `wait`: If true, the function will block until the timeout is reached.

- `function void say(string message)`

    Make Reynard say the specified message.
    - `message`: The message to say.

### Events

- `event new_message(string message)`

    Event that is fired when Reynard receives a new message from the user.
    - `message`: The message that Reynard received.

### Wires

- `wire ReynardState state [readonly]`

    The current state of Reynard. The state is updated at a fixed rate. The wire can be peeked, or can be
    connected to receive real-time updates.
