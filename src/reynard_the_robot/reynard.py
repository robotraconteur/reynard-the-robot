from aiohttp import web
import socketio
import asyncio
from threading import Thread, Lock, Event
import time

import importlib_resources
import numpy as np
import blinker

reynard_kinematics = {
    "body_offset": np.array([0, 70], dtype=np.float64),
    "bounds": np.array([[-1000, -500], [1000, 500]], dtype=np.float64),
    "p0": np.array([0, -95], dtype=np.float64),
    "p1": np.array([170, 0], dtype=np.float64),
    "p2": np.array([170, 0], dtype=np.float64),
    "p3": np.array([60, 0], dtype=np.float64),
    "q_bounds": np.array([[-10, -140, -175], [180, 140, 175]], dtype=np.float64),
    "vel_max": np.array([100, 100], dtype=np.float64),
    "q_vel_max": np.array([100, 100, 100], dtype=np.float64)
}


class Reynard:
    """
    The Reynard class implements Reynard the Robot. Reynard the Robot is a simple two dimensional 5 degree of 
    freedom cartoon robot. It is intended to be used as a simple target device for learning Robot Raconteur
    and other robotics software.

    The GUI interface is accessed using a standard web browser with the URL ``http://localhost:29201``. The
    host and port can be changed when constructing the Reynard object using the ``host`` and ``port`` parameters.

    Reynard the Robot is implemented as a simple web server using the aiohttp and python-socketio libraries. Reynard
    can be controlled directly using the Python API, or through the other communication methods provided by the
    Python package. Reynard the Robot provides the following interactions:

    - teleport: Move Reynard to a new position instantly
    - say: Make Reynard say a message
    - drive_robot: Drive Reynard's base in the x and y directions at a given velocity
    - set_arm_position: Set the position of Reynard's arm joints instantly
    - drive_arm: Drive Reynard's arm joints at a given velocity
    - arm_position: Get the current position of Reynard's arm joints
    - robot_position: Get the current position of Reynard's base
    - robot_velocity: Get the current velocity of Reynard's base
    - arm_velocity: Get the current velocity of Reynard's arm joints
    - time: Get the current simulation time in seconds
    - color: Get or set the color of Reynard's body as an RGB tuple between 0 and 1
    - new_message: Signal that is emitted when a new message is received from the API

    The Reynard class can be used with AIO or with the standard Python threading model. When used with AIO, the
    methods starting with ``aio_`` should be used. When used with the standard Python threading model, the methods
    without ``aio_`` should be used.

    The start or aio_start method must be called to start the Reynard server. The close method should be called
    to stop the Reynard server.

    :param host: The host to bind the Reynard server to. Default is localhost. Set to 0.0.0.0 to bind to all interfaces.
    :type host: str
    :param port: The port to bind the Reynard server to. Default is 29201.
    :type port: int
    """
    def __init__(self, host="localhost", port=29201):
        self.app = web.Application()
        self.aio_lock = asyncio.Lock()
        self.socketio = socketio.AsyncServer(async_mode='aiohttp')
        self.socketio.attach(self.app)
        self._host = host
        self._port = port
        self._loop = None
        self._started = Event()
        self._dt = 5e-2
        self._vel_loop_task = None

        self._pos = np.array([0, 0], dtype=np.float64)
        self._last_update_pos = np.copy(self._pos)
        self._q = np.array([0, 0, 0], dtype=np.float64)
        self._last_update_q = np.copy(self._q)
        self._vel = np.array([0, 0], dtype=np.float64)
        self._vel_stop_time = -1
        self._q_vel = np.array([0, 0, 0], dtype=np.float64)
        self._q_vel_stop_time = -1
        self._color = np.array([0.929, 0.49, 0.192], dtype=np.float64)

        self._new_message = blinker.signal('new_message')
        
        static_path = importlib_resources.files('reynard_the_robot').joinpath('web_static')

        async def serve(request):
            path = request.match_info.get('path', 'index.html')
            return web.FileResponse(static_path / path)

        self._register_api()
        self.app.router.add_get('/', serve)
        self.app.router.add_get('/{path:.*}', serve)

        self._api_msg_queue = asyncio.Queue()
        self.socketio.on('new_message', self._new_message_cb)


    def _new_message_cb(self, sid, message):
        self._new_message.send(None, message=message)
        self._api_msg_queue.put_nowait(message)

    async def aio_start(self):
        """
        AIO version of start. Must be called to start the Reynard server.
        Use with await in an async function.
        """
        self._runner = web.AppRunner(self.app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self._host, self._port)
        await self._site.start()

        self._vel_loop_task = asyncio.create_task(self._vel_loop())

    async def _vel_loop(self):
        while True:
            async with self.aio_lock:
                self._pos += self._vel*self._dt
                self._pos = np.clip(self._pos, reynard_kinematics["bounds"][0], reynard_kinematics["bounds"][1])
                self._q += self._q_vel*self._dt
                self._q = np.clip(self._q, reynard_kinematics["q_bounds"][0], reynard_kinematics["q_bounds"][1])
                t = time.perf_counter()
                if t > self._vel_stop_time and self._vel_stop_time >= 0:
                    self._vel = np.array([0, 0], dtype=np.float64)
                if t > self._q_vel_stop_time and self._q_vel_stop_time >= 0:
                    self._q_vel = np.array([0, 0, 0], dtype=np.float64)
                if np.linalg.norm(self._last_update_pos - self._pos) > 2 or np.any(np.abs(self._last_update_q - self._q) > 2):
                    self._last_update_pos = np.copy(self._pos)
                    self._last_update_q = np.copy(self._q)
                    await self.socketio.emit('update', {'x': self._pos[0], 'y': self._pos[1], 'q1': self._q[0], \
                                                           'q2': self._q[1], 'q3': self._q[2]})
            await asyncio.sleep(self._dt)

    async def aio_teleport(self, x, y):
        """
        AIO version of teleport. Teleport Reynard to a new position instantly.
        Use with await in an async function.

        :param x: The x position to teleport Reynard to in millimeters
        :type x: float
        :param y: The y position to teleport Reynard to in millimeters
        :type y: float
        """
        x,y = np.clip([x, y], reynard_kinematics["bounds"][0], reynard_kinematics["bounds"][1])
        async with self.aio_lock:
            self._vel = np.array([0, 0], dtype=np.float64)
            self._pos = np.array([x, y], dtype=np.float64)
            await self.socketio.emit('teleport', {'x': x, 'y': y})

    async def aio_say(self, message):
        """
        AIO version of say. Make Reynard say a message.
        Use with await in an async function.

        :param message: The message to say
        :type message: str
        """
        await self.socketio.emit('say', message)

    async def aio_set_arm_position(self, q1, q2, q3):
        """
        AIO version of set_arm_position. Set the position of Reynard's arm joints instantly.
        Use with await in an async function.

        :param q1: The position of the first arm joint in degrees
        :type q1: float
        :param q2: The position of the second arm joint in degrees
        :type q2: float
        :param q3: The position of the third arm joint in degrees
        :type q3: float
        """
        q1,q2,q3 = np.clip([q1,q2,q3], reynard_kinematics["q_bounds"][0], reynard_kinematics["q_bounds"][1])
        async with self.aio_lock:
            self._q_vel = np.array([0, 0, 0], dtype=np.float64)
            self._q = np.array([q1, q2, q3], dtype=np.float64)
            await self.socketio.emit('arm', {'q1': q1, 'q2': q2, 'q3': q3})

    async def aio_drive_robot(self, vel_x, vel_y, timeout=-1, wait=False):
        """
        AIO version of drive_robot. Drive Reynard's base in the x and y directions at a given velocity.
        Use with await in an async function.

        :param vel_x: The velocity in the x direction in millimeters per second
        :type vel_x: float
        :param vel_y: The velocity in the y direction in millimeters per second
        :type vel_y: float
        :param timeout: The time to drive Reynard at the given velocity. If timeout is greater than 0, Reynard will stop
                        after the given time. If timeout is less than 0, Reynard will continue indefinitely. Default is -1.
        :type timeout: float
        :param wait: If wait is True, the function will wait until the timeout has expired before returning. 
                     Default is False.
        """
        vel_x, vel_y = np.clip([vel_x, vel_y], -reynard_kinematics["vel_max"], reynard_kinematics["vel_max"])
        async with self.aio_lock:
            self._vel = np.array([vel_x, vel_y], dtype=np.float64)
            if timeout > 0:
                self._vel_stop_time = time.perf_counter() + timeout
            else:
                self._vel_stop_time = -1
        if wait:
            await asyncio.sleep(timeout)

    async def aio_drive_arm(self, q1, q2, q3, timeout=-1, wait=False):
        """
        AIO version of drive_arm. Drive Reynard's arm joints at a given angular velocity.
        Use with await in an async function.

        :param q1: The angular velocity of the first arm joint in degrees per second
        :type q1: float
        :param q2: The angular velocity of the second arm joint in degrees per second
        :type q2: float
        :param q3: The angular velocity of the third arm joint in degrees per second
        :type q3: float
        """
        q1,q2,q3 = np.clip([q1,q2,q3], -reynard_kinematics["q_vel_max"], reynard_kinematics["q_vel_max"])
        async with self.aio_lock:
            self._q_vel = np.array([q1, q2, q3], dtype=np.float64)
            if timeout > 0:
                self._q_vel_stop_time = time.perf_counter() + timeout
            else:
                self._q_vel_stop_time = -1
        if wait:
            await asyncio.sleep(timeout)

    async def aio_set_color(self, r, g, b):
        """
        "AIO version of property set color. Set the color of Reynard's body as an RGB tuple between 0 and 1.
        Use with await in an async function.

        :param r: The red component of the color between 0 and 1
        :type r: float
        :param g: The green component of the color between 0 and 1
        :type g: float
        :param b: The blue component of the color between 0 and 1
        :type b: float
        """
        r,g,b = np.clip([r,g,b], 0, 1.0)
        async with self.aio_lock:
            self._color = np.array([r, g, b], dtype=np.float64)
            await self.socketio.emit('color', {'r': r, 'g': g, 'b': b})

    def start(self):
        """
        Start the Reynard server. This synchronous method should be used with the standard Python threading model.
        A thread will be created to run the server. If you are using AIO, use aio_start instead. The AIO version
        will use the asyncio event loop to run the server instead of a thread.
        """
        self.thread = Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        self._started.wait()

    def _run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.set_debug(True)
        self._loop.run_until_complete(self.aio_start())
        self._started.set()
        self._loop.run_forever()

    def close(self):
        """
        Close the Reynard server. This synchronous method should be used with the standard Python threading model.
        This is not needed when using AIO.
        """
        if self._loop.is_running():
            self._loop.stop()

    def teleport(self, x, y):
        """
        Instantly move Reynard to a new position.

        :param x: The x position to teleport Reynard to in millimeters
        :type x: float
        :param y: The y position to teleport Reynard to in millimeters
        :type y: float
        """
        asyncio.run_coroutine_threadsafe(self.aio_teleport(x, y), self._loop).result()

    def say(self, message):
        """
        Make Reynard say a message.

        :param message: The message to say
        :type message: str
        """
        asyncio.run_coroutine_threadsafe(self.aio_say(message), self._loop).result()

    def set_arm_position(self, q1, q2, q3):
        """
        Instantly set the position of Reynard's arm joints.

        :param q1: The position of the first arm joint in degrees
        :type q1: float
        :param q2: The position of the second arm joint in degrees
        :type q2: float
        :param q3: The position of the third arm joint in degrees
        :type q3: float
        """
        asyncio.run_coroutine_threadsafe(self.aio_set_arm_position(q1, q2, q3), self._loop).result()

    def drive_robot(self, vel_x, vel_y, timeout = -1, wait = False):
        """
        Drive Reynard's base in the x and y directions at a given velocity.

        :param vel_x: The velocity in the x direction in millimeters per second
        :type vel_x: float
        :param vel_y: The velocity in the y direction in millimeters per second
        :type vel_y: float
        :param timeout: The time to drive Reynard at the given velocity. If timeout is greater than 0, Reynard will stop
                        after the given time. If timeout is less than 0, Reynard will continue indefinitely. Default is -1.
        :type timeout: float
        :param wait: If wait is True, the function will wait until the timeout has expired before returning.
                        Default is False.
        :type wait: bool
        """
        asyncio.run_coroutine_threadsafe(self.aio_drive_robot(vel_x, vel_y, timeout, wait), self._loop).result()

    def drive_arm(self, q1, q2, q3, timeout = -1, wait = False):
        """
        Drive Reynard's arm joints at a given angular velocity.

        :param q1: The angular velocity of the first arm joint in degrees per second
        :type q1: float
        :param q2: The angular velocity of the second arm joint in degrees per second
        :type q2: float
        :param q3: The angular velocity of the third arm joint in degrees per second
        :type q3: float
        :param timeout: The time to drive Reynard at the given velocity. If timeout is greater than 0, Reynard will stop
                        after the given time. If timeout is less than 0, Reynard will continue indefinitely. Default is -1.
        :type timeout: float
        :param wait: If wait is True, the function will wait until the timeout has expired before returning.
                        Default is False.
        """
        asyncio.run_coroutine_threadsafe(self.aio_drive_arm(q1, q2, q3, timeout, wait), self._loop).result()
       

    @property
    def arm_position(self):
        """
        Get the current position of Reynard's arm joints in degrees.
        """
        return self._q
    
    @property
    def robot_position(self):
        """
        Get the current position of Reynard's base.
        """
        return self._pos
    
    @property
    def robot_velocity(self):
        """
        Get the current velocity of Reynard's base.
        """
        return self._vel
    
    @property
    def arm_velocity(self):
        """
        Get the current velocity of Reynard's arm joints.
        """
        return self._q_vel
    
    @property
    def time(self):
        """
        Get the current simulation time in seconds. The simulation time starts at 0 when the server is started.
        """
        return time.perf_counter()
    
    @property
    def color(self):
        """
        Get or set the color of Reynard's body as an RGB tuple between 0 and 1. Use aio_set_color to set the color
        when using AIO.
        """
        return self._color
    
    @color.setter
    def color(self, color):
        asyncio.run_coroutine_threadsafe(self.aio_set_color(*color), self._loop).result()

    @property
    def new_message(self):
        """
        Event for new messages received from the API. Connect to this event to receive new messages. This property
        is a blinker signal. Use the connect method to connect to the signal.
        """
        return self._new_message
    
    def _register_api(self):
        async def api_get_messages(request):
            messages = []
            while not self._api_msg_queue.empty():
                messages.append(await self._api_msg_queue.get())
            return web.json_response(messages)
        
        async def api_post_teleport(request):
            json = await request.json()
            x = json["x"]
            y = json["y"]
            await self.aio_teleport(x, y)
            return web.Response()
        
        async def api_post_say(request):
            json = await request.json()
            message = json["message"]
            await self.aio_say(message)
            return web.Response()
        
        async def api_post_arm(request):
            json = await request.json()
            q1 = json["q1"]
            q2 = json["q2"]
            q3 = json["q3"]
            await self.aio_set_arm_position(q1, q2, q3)
            return web.Response()
        
        async def api_post_drive_robot(request):
            json = await request.json()
            vel_x = json["vel_x"]
            vel_y = json["vel_y"]
            timeout = float(json.get("timeout", -1))
            wait = bool(json.get("wait", False))
            await self.aio_drive_robot(vel_x, vel_y, timeout, wait)
            return web.Response()
        
        async def api_post_drive_arm(request):
            json = await request.json()
            q1 = json["q1"]
            q2 = json["q2"]
            q3 = json["q3"]
            timeout = float(json.get("timeout", -1))
            wait = bool(json.get("wait", False))
            await self.aio_drive_arm(q1, q2, q3, timeout, wait)
            return web.Response()
        
        async def api_post_color(request):
            json = await request.json()
            r = json["r"]
            g = json["g"]
            b = json["b"]
            await self.aio_set_color(r, g, b)
            return web.Response()
        
        async def api_get_state(request):
            res = {
                "time": self.time,
                "x": self._pos[0],
                "y": self._pos[1],
                "q1": self._q[0],
                "q2": self._q[1],
                "q3": self._q[2],
                "vel_x": self._vel[0],
                "vel_y": self._vel[1],
                "vel_q1": self._q_vel[0],
                "vel_q2": self._q_vel[1],
                "vel_q3": self._q_vel[2]
            }
            return web.json_response(res)
        
        async def api_get_color(request):
            res = {
                "r": self._color[0],
                "g": self._color[1],
                "b": self._color[2]
            }
            return web.json_response(res)
        
        async def api_set_arm_position(request):
            json = await request.json()
            q1 = json["q1"]
            q2 = json["q2"]
            q3 = json["q3"]
            await self.aio_set_arm_position(q1, q2, q3)
            return web.Response()
        
        self.app.router.add_get('/api/messages', api_get_messages)
        self.app.router.add_post('/api/teleport', api_post_teleport)
        self.app.router.add_post('/api/say', api_post_say)
        self.app.router.add_post('/api/arm', api_post_arm)
        self.app.router.add_post('/api/drive_robot', api_post_drive_robot)
        self.app.router.add_post('/api/drive_arm', api_post_drive_arm)
        self.app.router.add_post('/api/color', api_post_color)
        self.app.router.add_get('/api/state', api_get_state)
        self.app.router.add_get('/api/color', api_get_color)
        self.app.router.add_post('/api/set_arm_position', api_set_arm_position)



