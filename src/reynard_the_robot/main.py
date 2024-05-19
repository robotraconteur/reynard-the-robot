from .reynard import Reynard
from .ascii_socket import ReynardAsciiSocketServer
import drekar_launch_process
import time
from .robotraconteur import ReynardRobotRaconteurService
import sys
from .gui import ReynardGui
import argparse


def main():

    parser = argparse.ArgumentParser("reynard-the-robot")
    parser.add_argument("--gui", action="store_true", help="Run Reynard with QT GUI")
    parser.add_argument("--disable-robotraconteur", action="store_true", help="Disable Robot Raconteur service")
    parser.add_argument("--disable-ascii-socket", action="store_true", help="Disable ASCII socket server")
    parser.add_argument("--http-public", action="store_true", help="Use public IP for HTTP socket server")
    parser.add_argument("--http-port", type=int, default=29201, help="Port for HTTP socket server")
    parser.add_argument("--ascii-socket-public", action="store_true", help="Use public IP for ASCII socket server")
    parser.add_argument("--ascii-socket-port", type=int, default=29202, help="Port for ASCII socket server")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args, _ = parser.parse_known_args()

    reynard = None
    ascii_server = None
    rr_server = None
    try:
        reynard_host = "localhost"
        if args.http_public:
            reynard_host = ""
        reynard = Reynard(reynard_host, args.http_port)
        if not args.quiet:
            print(f"Reynard the Robot started on http://localhost:{args.http_port}")
            print()
        reynard.start()
        if not args.disable_ascii_socket:
            ascii_host = "localhost"
            if args.ascii_socket_public:
                ascii_host = ""
            ascii_server = ReynardAsciiSocketServer(reynard, ascii_host, args.ascii_socket_port)
            if not args.quiet:
                print(f"ASCII socket server started on port {args.ascii_socket_port}")
                print()
        if not args.disable_robotraconteur:
            rr_server = ReynardRobotRaconteurService(reynard, sys.argv)
            if not args.quiet:
                rr_server.print_info()
                print()
        if args.gui:
            if not ReynardGui.gui_available():
                raise Exception(
                    "GUI not available. Do not use --gui argument and use external web browser. Install pyside6 Python package to enable GUI.")
            gui = ReynardGui()
            gui.run_gui()
        else:
            if not args.quiet:
                print("Reynard the Robot started in headless mode. Press Ctrl+C to exit.")
            drekar_launch_process.wait_exit()
    finally:
        reynard.close()
        if ascii_server is not None:
            ascii_server.close()
        if rr_server is not None:
            rr_server.close()


if __name__ == "__main__":
    main()
