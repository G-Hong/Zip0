import sys
sys.path.append('/home/ghong/projects')
import nexodim as nxd

robot = nxd.robots.SO101(id="arm_1")
robot.connect(mode="teach")
robot.teleop()
robot.disconnect()