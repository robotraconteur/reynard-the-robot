# ASCII Socket Reference

Reynard the Robot provides an ASCII socket interface. The ASCII socket interface is a simple text-based interface that 
can be used to communicate with Reynard the Robot. ASCII interfaces are commonly found on industrial devices,
using both sockets and serial ports. The Reynard interface is designed to be representative of real devices that
use ASCII interfaces.

Many industrial devices also use binary protocols. Binary protocols are more efficient and can be more reliable,
but are more difficult to debug and understand. Binary protocols often require a client library to use.
Reynard the Robot does not provide a binary protocol, other than the Robot Raconteur service which can be
considered a binary protocol that is only used with the Robot Raconteur client library.

See the examples in the `examples` directory for examples of using the ASCII socket interface.

## Connecting to the ASCII Socket

Reynard the Robot listens to port 29201 for ASCII socket connections. This port may be changed by the user
when starting the server. The host is typically `localhost`, but may be changed to the IP address of the computer
running the service.

## Commands

Commands are sent to the ASCII socket as text strings. The commands are case-insensitive. A command is sent with
the command name, followed by a space, and then the parameters separated by spaces. A newline character is sent
at the end of the command. The response is `OK` if the command is successful followed by a newline character. If
an error occurs, `ERROR` is returned with a description of the error, followed by a newline character. Some commands
may replace `OK` with a response string followed by parameters and a newline character.

In python it is recommended that the `shlex` module be used to parse the command strings.

### TELEPORT

The `TELEPORT` command is used to instantly move Reynard to a new position.

```
TELEPORT <x> <y>
```

- `x` (float): The x position in millimeters
- `y` (float): The y position in millimeters

Returns `OK` if successful.

Example:

```
TELEPORT 0.5 0.5
```

### SAY

The `SAY` command is used to make Reynard say a message.

```
SAY "<message>"
```

- `message` (string): The message to say

Returns `OK` if successful.

Example:

```
SAY "Hello, World!"
```

### SETARM

The `SETARM` command is used to instantly set the position of Reynard's arm joints.

```
SETARM <q1> <q2> <q3>
```

- `q1` (float): The position of joint 1 in degrees
- `q2` (float): The position of joint 2 in degrees
- `q3` (float): The position of joint 3 in degrees

Returns `OK` if successful.

Example:

```
SETARM 100 -30 -70
```

### DRIVE

The `DRIVE` command is used to drive Reynard's base in the x and y directions at a given velocity.

```
DRIVE <vel_x> <vel_y> <timeout> <wait>
```

- `vel_x` (float): The x velocity in millimeters per second
- `vel_y` (float): The y velocity in millimeters per second
- `timeout` (float): The time in seconds to drive the robot
- `wait` (bool): If `1`, the command will block until the drive is complete. If `0`, the command will return immediately.

`timeout` and `wait` are optional.

Returns `OK` if successful.

Example:

```
DRIVE 500 -200
```

### DRIVEARM

The `DRIVEARM` command is used to drive Reynard's arm joints to a specified angular velocity.

```
DRIVERARM <q1> <q2> <q3> <timeout> <wait>
```

- `q1` (float): The angular velocity of joint 1 in degrees per second
- `q2` (float): The angular velocity of joint 2 in degrees per second
- `q3` (float): The angular velocity of joint 3 in degrees per second
- `timeout` (float): The time in seconds to drive the robot
- `wait` (bool): If `1`, the command will block until the drive is complete. If `0`, the command will return immediately.

`timeout` and `wait` are optional.

Returns `OK` if successful.

Example:

```
DRIVEARM 10 -30 -15
```

### GETCOLOR

The `GETCOLOR` command is used to get the Reynard's current color.

```
COLORGET
```

Returns `COLOR <r> <g> <b>` if successful.

- `r` (float): The red component of the color between 0 and 1
- `g` (float): The green component of the color between 0 and 1
- `b` (float): The blue component of the color between 0 and 1

Example:

```
COLORGET
```

Response:

```
COLOR 1 0 0
```

### SETCOLOR

The `SETCOLOR` command is used to set Reynard's color.

```
COLORSET <r> <g> <b>
```

- `r` (float): The red component of the color between 0 and 1
- `g` (float): The green component of the color between 0 and 1
- `b` (float): The blue component of the color between 0 and 1

Returns `OK` if successful.

Example:

```
COLORSET 0 1 0
```

### STATE

The `STATE` command is used to get the current state of Reynard.

```
STATE
```

Returns `STATE <x> <y> <q1> <q2> <q3>` if successful.

- `x` (float): The x position in millimeters
- `y` (float): The y position in millimeters
- `q1` (float): The position of joint 1 in degrees
- `q2` (float): The position of joint 2 in degrees
- `q3` (float): The position of joint 3 in degrees

### MESSAGE

The `MESSAGE` command is used to read a single message sent to Reynard.

```
MESSAGE
```

Returns `MESSAGE <message>` if successful, `NOMESSAGE` if no message is available, or `ERROR` if an error occurs.

Example:

```
MESSAGE
```

Response:

```
MESSAGE "Hello, World!"
```
