from .reynard import Reynard
from .ascii_socket import ReynardAsciiSocketServer
import drekar_launch_process
import time

def main():
    reynard = Reynard()
    reynard.start()
    ascii_server = ReynardAsciiSocketServer(reynard)
    drekar_launch_process.wait_exit()
    reynard.close()
    ascii_server.close()

if __name__ == "__main__":
    main()