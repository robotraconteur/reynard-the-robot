import socket
import time
import shlex

# Connect the socket
s = socket.create_connection(("localhost", 29202))
s.settimeout(5)

# Create the file-like object
f = s.makefile("rw")

# Read the state
f.writelines(["STATE\n"])
f.flush()
state_str = f.readline().strip()
state_str_p = shlex.split(state_str)
assert state_str_p[0] != "ERROR"
print(f"Robot position: {float(state_str_p[1])}, {float(state_str_p[2])}")
print(f"Arm position: {float(state_str_p[3])}, {float(state_str_p[4])}, {float(state_str_p[5])}")

# Teleport the robot
f.writelines(["TELEPORT 100 -200\n"])
f.flush()
assert f.readline().strip() == "OK"

# Drive the robot
f.writelines(["DRIVE 500 -200\n"])
f.flush()
assert f.readline().strip() == "OK"

time.sleep(1)

# Stop the robot
f.writelines(["DRIVE 0 0\n"])
f.flush()
assert f.readline().strip() == "OK"

# Set the arm position
f.writelines(["SETARM 100 -30 -70\n"])
f.flush()
assert f.readline().strip() == "OK"

# Drive the arm
f.writelines(["DRIVEARM 10 -30 -15\n"])
f.flush()
assert f.readline().strip() == "OK"

time.sleep(1)

# Stop the arm
f.writelines(["DRIVEARM 0 0 0\n"])
f.flush()
assert f.readline().strip() == "OK"

# Read the color

f.writelines(["COLORGET\n"])
f.flush()
color_str = f.readline().strip()
color_str_p = shlex.split(color_str)
assert color_str_p[0] != "ERROR"
print(f"Color: {float(color_str_p[1])}, {float(color_str_p[2])}, {float(color_str_p[3])}")

# Set the color
f.writelines(["COLORSET 1 0 0\n"])
f.flush()
assert f.readline().strip() == "OK"

time.sleep(1)

# Reset the color
f.writelines(["COLORSET 0.929 0.49 0.192\n"])
f.flush()
assert f.readline().strip() == "OK"

# Say hello
f.writelines(["SAY \"Hello World From Socket!\"\n"])
f.flush()
assert f.readline().strip() == "OK"

# Read any messages
while True:
    f.writelines(["MESSAGE\n"])
    f.flush()
    msg_res_str = f.readline().strip()
    msg_res_str_p = shlex.split(msg_res_str)
    assert msg_res_str_p[0] != "ERROR"
    if msg_res_str_p[0] == "NOMESSAGE":
        break
    print(f"New message: {msg_res_str_p[1]}")
