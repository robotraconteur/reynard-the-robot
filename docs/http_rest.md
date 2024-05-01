# REST API Reference

Reynard the Robot provides an HTTP REST API. The REST API exposes most of the basic functionality.

## Base URL

The default base URL is:

```
http://localhost:29201/api
```

The `localhost` and `29201` port may vary depending on the port specified to start the HTTP server or 
the IP address of the computer running the server.

## Endpoints

### Teleport the Robot

```
POST /teleport
```

### Description

Instantly move Reynard to a new position.

#### Parameters

- `x` (float): The x position in millimeters
- `y` (float): The y position in millimeters

#### Response

None

#### Example

Example Request:

```bash
curl -X POST http://localhost:29201/api/teleport -d '{ "x": 0.5, "y": 0.5}'
```

### Say a Message

```
POST /say
```

#### Description

Make Reynard say a message.

#### Parameters

- `message` (string): The message to say

#### Response

None

#### Example

Example Request:

```bash
curl -X POST http://localhost:29201/api/say -d '{ "message": "Hello, World!"}'
```

### Set the Arm Position

```bash
POST /arm
```

#### Description

Instantly set the position of Reynard's arm joints.

#### Parameters

- `q1` (float): The position of the first joint in degrees
- `q2` (float): The position of the second joint in degrees
- `q3` (float): The position of the third joint in degrees

#### Response

None

#### Example

Example Request:

```bash
curl -X POST http://localhost:29201/api/arm -d '{ "q1": 30, "q2": -30, "q3": -90}'
```

### Drive the Robot

```
POST /drive_robot
```

#### Description

Drive Reynard's base in the x and y directions at a given velocity.

#### Parameters

- `vel_x` (float): The x velocity in millimeters per second
- `vel_y` (float): The y velocity in millimeters per second


#### Response

None

#### Example

Example Request:

```bash
curl -X POST http://localhost:29201/api/drive_robot -d '{ "vel_x": 100, "vel_y": 100}'
```

### Drive the Arm

```
POST /drive_arm
```

#### Description

Drive Reynard's arm joints at a given angular velocity.

#### Parameters

- `q1` (float): The angular velocity of the first joint in degrees per second
- `q2` (float): The angular velocity of the second joint in degrees per second
- `q3` (float): The angular velocity of the third joint in degrees per second

#### Response

None

#### Example

Example Request:

```bash
curl -X POST http://localhost:29201/api/drive_arm -d '{ "q1": 10, "q2": -30, "q3": -15}'
```

#### Get the Color

```
GET /color
```

#### Description

Get the current color in RGB between 0 and 1.

#### Response

- `r` (float): The red component of the color
- `g` (float): The green component of the color
- `b` (float): The blue component of the color

#### Example

Example Request:

```bash
curl http://localhost:29201/api/color
```

Example Response:

```json
{
    "r": 0.929,
    "g": 0.49,
    "b": 0.192
}
```
### Set the Color

```
POST /color
```

#### Description

Set Reynard's color in RGB between 0 and 1.

#### Parameters

- `r` (float): The red component of the color
- `g` (float): The green component of the color
- `b` (float): The blue component of the color

#### Response

None

#### Example

Example Request:

```bash
curl -X POST http://localhost:29201/api/color -d '{ "r": 1, "g": 0, "b": 0}'
```

### Get the State

```
GET /state
```

#### Description

Get the current state of Reynard position and arm joints.

#### Response

- `x` (float): The x position in millimeters
- `y` (float): The y position in millimeters
- `q1` (float): The position of the first joint in degrees
- `q2` (float): The position of the second joint in degrees
- `q3` (float): The position of the third joint in degrees

#### Example

Example Request:

```bash
curl http://localhost:29201/api/state
```

Example Response:

```json
{
    "x": 0.5,
    "y": 0.5,
    "q1": 30,
    "q2": -30,
    "q3": -90
}
```

### Messages

```
GET /messages
```

#### Description

Get the list of messages that Reynard has received from the user.

#### Response

A list of messages

#### Example

Example Request:

```bash
curl http://localhost:29201/api/messages
```

Example Response:

```json
[
    "Hello, Reynard!",
    "Hello, Reynard Again!"
]
```
