from .reynard import Reynard
import drekar_launch_process
import time

def main():
    reynard = Reynard()
    reynard.start()
    while True:
        reynard.teleport(0, 0)
        reynard.move_arm(0, 0, 0)
        time.sleep(1)
        reynard.teleport(-100, -200)
        reynard.move_arm(100, -30, -70)
        time.sleep(1)
        reynard.say("Hello, World!")
    drekar_launch_process.wait_exit()
    reynard.stop()

if __name__ == "__main__":
    main()