import socket
import time
import threading
import select
import weakref
from contextlib import suppress
import shlex
import queue

class ReynardAsciiSocketConnection:
    def __init__(self, reynard, s):
        self._reynard = reynard
        self._s = s
        self._f = s.makefile(mode='rw')

        self._message_queue = queue.Queue(10)
        
        self._reynard.new_message.connect(self._new_message)

        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def _new_message(self, _, message):
        self._message_queue.put_nowait(message)

    def _run(self):
        while True:
            l = None
            try:
                l = self._f.readline()
            except (ConnectionResetError,ConnectionAbortedError):
                return
            ret = None
            if l is None:
                return
            
            try:
                s1 = shlex.split(l)
                if s1[0] == "TELEPORT":
                    assert len(s1) == 3
                    x = float(s1[1])
                    y = float(s1[2])
                    self._reynard.teleport(x,y)
                    ret = "OK\n"
                elif s1[0] == "SAY":
                    assert len(s1) == 2
                    msg = s1[1]
                    self._reynard.say(msg)
                    ret = "OK\n"
                elif s1[0] == "SETARM":
                    assert len(s1) == 4
                    q1 = float(s1[1])
                    q2 = float(s1[2])
                    q3 = float(s1[3])
                    self._reynard.set_arm_position(q1, q2, q3)
                    ret = "OK\n"
                elif s1[0] == "DRIVE":
                    assert len(s1) >= 3
                    vel_x = float(s1[1])
                    vel_y = float(s1[2])
                    timeout = -1
                    if len(s1) >= 4:
                        timeout = float(s1[3])
                    wait = False
                    if len(s1) >= 5:
                        wait = bool(s1[4])
                    self._reynard.drive_robot(vel_x, vel_y, timeout, wait)
                    ret = "OK\n"
                elif s1[0] == "DRIVEARM":
                    assert len(s1) >= 4
                    q1 = float(s1[1])
                    q2 = float(s1[2])
                    q3 = float(s1[3])
                    timeout = -1
                    if len(s1) >= 5:
                        timeout = float(s1[4])
                    wait = False
                    if len(s1) >= 6:
                        wait = bool(s1[5])
                    self._reynard.drive_arm(q1, q2, q3, timeout, wait)
                    ret = "OK\n"
                elif s1[0] == "STATE":
                    assert len(s1) == 1
                    t = self._reynard.time
                    p = self._reynard.robot_position
                    a = self._reynard.arm_position
                    ret = f"STATE {t} {p[0]} {p[1]} {a[0]} {a[1]} {a[2]}\n"
                elif s1[0] == "COLORGET":
                    assert len(s1) == 1
                    c = self._reynard.color
                    ret = f"COLOR {c[0]} {c[1]} {c[2]}\n"
                elif s1[0] == "COLORSET":
                    assert len(s1) == 4
                    r = float(s1[1])
                    g = float(s1[2])
                    b = float(s1[3])
                    self._reynard.color = (r,g,b)
                    ret = "OK\n"
                elif s1[0] == "MESSAGE":
                    assert len(s1) == 1
                    try:
                        msg = self._message_queue.get_nowait()
                    except queue.Empty:
                        ret = "NOMESSAGE\n"
                    else:
                        ret = f"MESSAGE \"{msg}\"\n"
                else:
                    assert False, "Invalid command"
                    
            except Exception as e:
                ret = f"ERROR {repr(e)}\n"

            try:
                self._f.writelines([ret])
                self._f.flush()
            except:
                return
    


    def close(self):
        self._s.close()

class ReynardAsciiSocketServer:
    def __init__(self, reynard, host="localhost", port=29202):
        self._keepgoing = True
        self._reynard = reynard
        self._host = host
        self._port = port
        self._connections = weakref.WeakSet()

        self._s_server = socket.create_server((host,port))
        self._s_server.listen()

        self._thread = threading.Thread(target = self._run)
        self._thread.daemon = True
        self._thread.start()
    
    def _run(self):
        while self._keepgoing:
            try:
                s, _ = self._s_server.accept()
                if not s:
                    return
                c = ReynardAsciiSocketConnection(self._reynard, s)
                self._connections.add(c)
            except Exception:
                if not self._keepgoing:
                    return
                else:
                    raise

    def close(self):
        self._keepgoing = False
        self._s_server.close()

        connections = list(self._connections)
        for s in connections:
            with suppress(Exception):
                s.close()
            