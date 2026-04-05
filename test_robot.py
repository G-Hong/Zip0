import sys
import cv2
sys.path.append('/home/ghong/projects')
import nexodim as nxd

robot = nxd.robots.SO101()
robot.connect(mode="teach", use_camera=False)
robot.teleop()
robot.disconnect()