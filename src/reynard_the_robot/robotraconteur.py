import RobotRaconteur as RR
import threading
import numpy as np

_reynard_robdef = """
service experimental.reynard_the_robot

stdver 0.10

struct ReynardState
    field double time
    field double[] robot_position
    field double[] arm_position
    field double[] robot_velocity
    field double[] arm_velocity
end

object Reynard

    function void teleport(double x, double y)

    function void setf_arm_position(double q1, double q2, double q3)

    function double[] getf_arm_position()

    property double[] robot_position [readonly]

    function void drive_robot(double vel_x, double vel_y, double timeout, bool wait)

    function void drive_arm(double q1, double q2, double q3, double timeout, bool wait)

    function void say(string message)

    property double[] color

    wire ReynardState state [readonly]

    event new_message(string message)
end
"""

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

    def _new_message(self,_, message):
        self.new_message.fire(message)

    def teleport(self, x, y):
        with self._lock:
            if x > 1 or x < -1 or y > 0.5 or y < -0.5:
                raise RR.InvalidArgumentException("Teleport target position is out of range")
            # Convert from m to mm
            x1 = x*1e3
            y1 = y*1e3
            self._reynard.teleport(x1,y1)

    def setf_arm_position(self, q1, q2, q3):
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
        return np.array(self._reynard.robot_position,dtype=np.float64)*1e-3
    
    def drive_robot(self, vel_x, vel_y, timeout, wait):
        vel_x_1 = vel_x*1e3
        vel_y_1 = vel_y*1e3
        self._reynard.drive_robot(vel_x_1, vel_y_1, timeout, wait)

    def drive_arm(self, q1, q2, q3, timeout, wait):
        q1_1 = np.rad2deg(q1)
        q2_1 = np.rad2deg(q2)
        q3_1 = np.rad2deg(q3)

        self._reynard.drive_arm(q1_1, q2_1, q3_1, timeout, wait)

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
        if np.any(np.array(c) < 0) or np.any(np.array(c) > 1):
            raise RR.InvalidArgumentException("Invalid color value")        
        self._reynard.color = c

    def _timer_cb(self, evt):
        s = self._reynard_state_type()
        s.time = self._reynard.time
        s.robot_position = np.array(self._reynard.robot_position,dtype=np.float64)
        s.arm_position = np.array(self._reynard.arm_position,dtype=np.float64)
        s.robot_velocity = np.array(self._reynard.robot_velocity,dtype=np.float64)
        s.arm_velocity = np.array(self._reynard.arm_velocity,dtype=np.float64)

        self.state.OutValue = s


class ReynardRobotRaconteurService:
    def __init__(self, reynard, argv):

        self._node = RR.RobotRaconteurNode()
        self._node.Init()

        self._node.RegisterServiceType(_reynard_robdef)

        self._obj = ReynardImpl(reynard,self._node)

        self._node_setup = RR.ServerNodeSetup("experimental.reynard_the_robot", 29200, node = self._node, argv=argv)

        self._ctx = self._node.RegisterService("reynard", "experimental.reynard_the_robot.Reynard", self._obj)

    def close(self):
        self._node_setup.close()

    def print_info(self):
        print("Robot Raconteur service connection URLs:")
        for conn in self._ctx.GetCandidateConnectionURLs():
            print(f"    {conn}")
        print()
        print("Use the Robot Raconteur service browser to help find the service on a network. See: https://github.com/robotraconteur/RobotRaconteur_ServiceBrowser")


