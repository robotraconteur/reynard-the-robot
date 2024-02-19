from .reynard import Reynard
from .ascii_socket import ReynardAsciiSocketServer
import drekar_launch_process
import time
from .robotraconteur import ReynardRobotRaconteurService
import sys
from .gui import ReynardGui

def main():
    reynard = None
    ascii_server = None
    rr_server = None
    try:
        reynard = Reynard()
        reynard.start()
        ascii_server = ReynardAsciiSocketServer(reynard)
        rr_server = ReynardRobotRaconteurService(reynard,sys.argv)
        drekar_launch_process.wait_exit()
    finally:
        reynard.close()
        if ascii_server is not None:
            ascii_server.close()
        if rr_server is not None:
            rr_server.close()

if __name__ == "__main__":
    main()