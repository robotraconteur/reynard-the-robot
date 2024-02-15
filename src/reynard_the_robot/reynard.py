from aiohttp import web
import socketio
import asyncio
from threading import Thread, Lock, Event

import importlib_resources


class Reynard:
    def __init__(self, host="localhost", port=25000):
        self.app = web.Application()
        self.lock = Lock()
        self.socketio = socketio.AsyncServer(async_mode='aiohttp')
        self.socketio.attach(self.app)
        self._host = host
        self._port = port
        self._loop = None
        self._started = Event()

        static_path = importlib_resources.files('reynard_the_robot').joinpath('web_static')

        async def serve(request):
            path = request.match_info.get('path', 'index.html')
            return web.FileResponse(static_path / path)

        self.app.router.add_get('/', serve)
        self.app.router.add_get('/{path:.*}', serve)

        self.socketio.on('new_message', self.new_message)


    async def aio_start(self):
        self._runner = web.AppRunner(self.app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self._host, self._port)
        await self._site.start()

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
        with self.lock:
            asyncio.run_coroutine_threadsafe(self.socketio.emit('teleport', {'x': x, 'y': y}), self._loop).result()

    def say(self, message):
        with self.lock:
            asyncio.run_coroutine_threadsafe(self.socketio.emit('say', message), self._loop).result()

    def move_arm(self, q1, q2, q3):
        with self.lock:
            asyncio.run_coroutine_threadsafe(self.socketio.emit('arm', {'q1': q1, 'q2': q2, 'q3': q3}), self._loop).result()

    def new_message(self, sid, msg):
        print(msg)
