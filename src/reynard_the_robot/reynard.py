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
    def __init__(self, host="localhost", port=25000):
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

        self.app.router.add_get('/', serve)
        self.app.router.add_get('/{path:.*}', serve)

        self.socketio.on('new_message', self._new_message_cb)

    def _new_message_cb(self, sid, message):
        self._new_message.send(message)


    async def aio_start(self):
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
                if t > self._vel_stop_time:
                    self._vel = np.array([0, 0], dtype=np.float64)
                if t > self._q_vel_stop_time:
                    self._q_vel = np.array([0, 0, 0], dtype=np.float64)
                if np.linalg.norm(self._last_update_pos - self._pos) > 2 or np.any(np.abs(self._last_update_q - self._q) > 2):
                    self._last_update_pos = np.copy(self._pos)
                    self._last_update_q = np.copy(self._q)
                    await self.socketio.emit('update', {'x': self._pos[0], 'y': self._pos[1], 'q1': self._q[0], \
                                                           'q2': self._q[1], 'q3': self._q[2]})
            await asyncio.sleep(self._dt)

    async def aio_teleport(self, x, y):
        x,y = np.clip([x, y], reynard_kinematics["bounds"][0], reynard_kinematics["bounds"][1])
        async with self.aio_lock:
            self._vel = np.array([0, 0], dtype=np.float64)
            self._pos = np.array([x, y], dtype=np.float64)
            await self.socketio.emit('teleport', {'x': x, 'y': y})

    async def aio_say(self, message):
        await self.socketio.emit('say', message)

    async def aio_set_arm_position(self, q1, q2, q3):
        q1,q2,q3 = np.clip([q1,q2,q3], reynard_kinematics["q_bounds"][0], reynard_kinematics["q_bounds"][1])
        async with self.aio_lock:
            self._q_vel = np.array([0, 0, 0], dtype=np.float64)
            self._q = np.array([q1, q2, q3], dtype=np.float64)
            await self.socketio.emit('arm', {'q1': q1, 'q2': q2, 'q3': q3})

    async def aio_drive_robot(self, vel_x, vel_y, timeout=-1, wait=False):
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
        r,g,b = np.clip([r,g,b], 0, 1.0)
        async with self.aio_lock:
            self._color = np.array([r, g, b], dtype=np.float64)
            await self.socketio.emit('color', {'r': r, 'g': g, 'b': b})

    def start(self):
        self.thread = Thread(target=self._run)
        self.thread.start()
        self._started.wait()

    def _run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.set_debug(True)
        self._loop.run_until_complete(self.aio_start())
        self._started.set()
        self._loop.run_forever()

    def stop(self):
        if self._loop.is_running():
            self._loop.stop()

    def teleport(self, x, y):
        asyncio.run_coroutine_threadsafe(self.aio_teleport(x, y), self._loop).result()

    def say(self, message):
        asyncio.run_coroutine_threadsafe(self.aio_say(message), self._loop).result()

    def set_arm_position(self, q1, q2, q3):
        asyncio.run_coroutine_threadsafe(self.aio_set_arm_position(q1, q2, q3), self._loop).result()

    def drive_robot(self, vel_x, vel_y, timeout = -1, wait = False):
        asyncio.run_coroutine_threadsafe(self.aio_drive_robot(vel_x, vel_y, timeout, wait), self._loop).result()

    def drive_arm(self, q1, q2, q3, timeout = -1, wait = False):
        asyncio.run_coroutine_threadsafe(self.aio_drive_arm(q1, q2, q3, timeout, wait), self._loop).result()
       

    @property
    def arm_position(self):
        return self._q
    
    @property
    def robot_position(self):
        return self._pos
    
    @property
    def robot_velocity(self):
        return self._vel
    
    @property
    def arm_velocity(self):
        return self._q_vel
    
    @property
    def time(self):
        return time.perf_counter()
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        asyncio.run_coroutine_threadsafe(self.aio_set_color(*color), self._loop).result()

    @property
    def new_message(self):
        return self._new_message
