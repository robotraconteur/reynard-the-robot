from .reynard import Reynard
import drekar_launch_process
import time

def new_message(msg):
    print(msg + " in callback")

def main():
    reynard = Reynard()
    reynard.start()
    reynard.new_message.connect(new_message)
    drekar_launch_process.wait_exit()
    reynard.stop()

if __name__ == "__main__":
    main()