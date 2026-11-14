import RobotRaconteur as RR
import threading
import numpy as np

_reynard_robdef = """
## Reynard the Robot, a simulated 2D cartoon robot for learning Robot Raconteur.
## A mobile base carries a 3 joint planar arm. The GUI is at http://localhost:29201.
##
## Units are SI: meters, seconds, radians. The room is 2 m x 1 m with the origin
## at its center, +x right and +y up. The base position x is limited to -1 to 1 m,
## and y to -0.5 to 0.5 m.
##
## Kinematics: the shoulder (joint 1) is 0.095 m above the base position. Link 1
## and link 2 are 0.17 m, and the tool is 0.06 m. Joint angles are relative to
## the previous link, counterclockwise positive, and all zero points the arm to +x.
## Tool tip = base + (0, 0.095) + 0.17*[cos(q1), sin(q1)]
## + 0.17*[cos(q1+q2), sin(q1+q2)] + 0.06*[cos(q1+q2+q3), sin(q1+q2+q3)]
##
## Joint limits: q1 -0.17 to 3.14 rad, q2 -2.44 to 2.44 rad, q3 -3.05 to 3.05 rad.
## Speed limits: 0.1 m/s for each base axis and 1.75 rad/s for each joint.
service experimental.reynard_the_robot

stdver 0.10

## State of Reynard, updated every 0.05 s
struct ReynardState
    ## Time in seconds from an arbitrary start
    field double time
    ## Base position [x, y] in m
    field double[] robot_position
    ## Arm joint angles [q1, q2, q3] in rad
    field double[] arm_position
    ## Base velocity [vx, vy] in m/s
    field double[] robot_velocity
    ## Arm joint velocities [q1, q2, q3] in rad/s
    field double[] arm_velocity
end

## Reynard the Robot
object Reynard

    ## Move the base instantly to (x, y) in m, and stop it.
    ## Raises an error if the position is outside the room.
    function void teleport(double x, double y)

    ## Set the arm joint angles instantly, in rad. Values are clamped to the joint limits.
    function void setf_arm_position(double q1, double q2, double q3)

    ## Arm joint angles [q1, q2, q3] in rad
    function double[] getf_arm_position()

    ## Base position [x, y] in m
    property double[] robot_position [readonly]

    ## Drive the base at (vel_x, vel_y) in m/s, clamped to 0.1 m/s per axis.
    ## It stops at the room edges, and after timeout s, or never if timeout < 0.
    ## If wait is true, returns after timeout.
    function void drive_robot(double vel_x, double vel_y, double timeout, bool wait)

    ## Drive the arm joints at velocities q1, q2, q3 in rad/s, clamped to 1.75 rad/s.
    ## Joints stop at their limits, and after timeout s, or never if timeout < 0.
    ## If wait is true, returns after timeout.
    function void drive_arm(double q1, double q2, double q3, double timeout, bool wait)

    ## Stop the base and the arm at once, ending any drive_robot or drive_arm
    function void stop()

    ## Show a speech bubble with the message in the GUI
    function void say(string message)

    ## Body color [r, g, b], each 0 to 1
    property double[] color

    ## Robot state, updated every 0.05 s
    wire ReynardState state [readonly]

    ## A message typed by the user in the GUI
    event new_message(string message)
end
"""


def _check_finite(*values):
    # NaN compares false with everything, so it would pass any range check
    if not np.all(np.isfinite(values)):
        raise RR.InvalidArgumentException("Values must be finite numbers")


class ReynardImpl:

    def __init__(self, reynard, node=None):
        if node is None:
            self._node = RR.RobotRaconteurNode.s
        else:
            self._node = node

        self._reynard = reynard
        self._lock = threading.Lock()

        self._reynard_state_type = self._node.GetStructureType("experimental.reynard_the_robot.ReynardState")

        self.new_message = RR.EventHook()

        reynard.new_message.connect(self._new_message)

        self._state_timer = None

    def RRServiceObjectInit(self, ctx, path):
        self._state_timer = self._node.CreateTimer(0.05, self._timer_cb, False)
        self._state_timer.Start()

    def _new_message(self, _, message):
        self.new_message.fire(message)

    def teleport(self, x, y):
        _check_finite(x, y)
        with self._lock:
            if x > 1 or x < -1 or y > 0.5 or y < -0.5:
                raise RR.InvalidArgumentException("Teleport target position is out of range")
            # Convert from m to mm
            x1 = x * 1e3
            y1 = y * 1e3
            self._reynard.teleport(x1, y1)

    def setf_arm_position(self, q1, q2, q3):
        _check_finite(q1, q2, q3)
        with self._lock:
            # Convert from radians to degrees
            q1_1 = np.rad2deg(q1)
            q2_1 = np.rad2deg(q2)
            q3_1 = np.rad2deg(q3)
            self._reynard.set_arm_position(q1_1, q2_1, q3_1)

    def getf_arm_position(self):
        return np.deg2rad(self._reynard.arm_position)

    @property
    def robot_position(self):
        return np.array(self._reynard.robot_position, dtype=np.float64) * 1e-3

    def drive_robot(self, vel_x, vel_y, timeout, wait):
        _check_finite(vel_x, vel_y, timeout)
        vel_x_1 = vel_x * 1e3
        vel_y_1 = vel_y * 1e3
        self._reynard.drive_robot(vel_x_1, vel_y_1, timeout, wait)

    def drive_arm(self, q1, q2, q3, timeout, wait):
        _check_finite(q1, q2, q3, timeout)
        q1_1 = np.rad2deg(q1)
        q2_1 = np.rad2deg(q2)
        q3_1 = np.rad2deg(q3)

        self._reynard.drive_arm(q1_1, q2_1, q3_1, timeout, wait)

    def stop(self):
        self._reynard.stop()

    def say(self, message):
        self._reynard.say(message)

    @property
    def color(self):
        with self._lock:
            return self._reynard.color

    @color.setter
    def color(self, c):
        if len(c) != 3:
            raise RR.InvalidArgumentException("Expected an array with length of 3")
        _check_finite(*c)
        if np.any(np.array(c) < 0) or np.any(np.array(c) > 1):
            raise RR.InvalidArgumentException("Invalid color value")
        self._reynard.color = c

    def _timer_cb(self, evt):
        s = self._reynard_state_type()
        s.time = self._reynard.time
        # Convert from mm to m, and from degrees to radians
        s.robot_position = np.array(self._reynard.robot_position, dtype=np.float64) * 1e-3
        s.arm_position = np.deg2rad(np.array(self._reynard.arm_position, dtype=np.float64))
        s.robot_velocity = np.array(self._reynard.robot_velocity, dtype=np.float64) * 1e-3
        s.arm_velocity = np.deg2rad(np.array(self._reynard.arm_velocity, dtype=np.float64))

        self.state.OutValue = s


class ReynardRobotRaconteurService:
    def __init__(self, reynard, argv):

        self._node = RR.RobotRaconteurNode()
        self._node.Init()

        self._node.RegisterServiceType(_reynard_robdef)

        self._obj = ReynardImpl(reynard, self._node)

        self._node_setup = RR.ServerNodeSetup("experimental.reynard_the_robot", 29200, node=self._node, argv=argv)

        self._ctx = self._node.RegisterService("reynard", "experimental.reynard_the_robot.Reynard", self._obj)

    def close(self):
        self._node_setup.close()

    def print_info(self):
        print("Robot Raconteur service connection URLs:")
        for conn in self._ctx.GetCandidateConnectionURLs():
            print(f"    {conn}")
        print()
        print("Use the Robot Raconteur service browser to help find the service on a network. See: https://github.com/robotraconteur/RobotRaconteur_ServiceBrowser")
