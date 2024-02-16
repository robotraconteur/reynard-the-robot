from .reynard import Reynard
import drekar_launch_process
import time

def new_message(msg):
    print(msg + " in callback")

def main():
    reynard = Reynard()
    reynard.start()
    reynard.new_message.connect(new_message)
    while True:
        # reynard.teleport(0, 0)
        reynard.drive_robot(50, -200, 1, False)
        # reynard.set_arm_position(0, 0, 0)
        reynard.drive_arm(0, 0, 0, 1, False)
        reynard.color = (1, 0, 0)
        time.sleep(1)
        # reynard.teleport(-100, -200)
        reynard.drive_robot(-200, 100, 1, False)
        reynard.drive_arm(10, 20, 40, 1, False)
        # reynard.set_arm_position(100, -30, -70)
        reynard.color = (0, 1, 0)
        time.sleep(1)
        reynard.say("Hello, World!")
    drekar_launch_process.wait_exit()
    reynard.stop()

if __name__ == "__main__":
    main()