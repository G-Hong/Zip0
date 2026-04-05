import sys
import json
sys.path.append('/home/ghong/projects')
import nexodim as nxd

robot = nxd.robots.SO101()
robot.connect(mode="teach", use_camera=False)

motor_names = ["shoulder_pan", "shoulder_lift", "elbow_flex",
               "wrist_flex", "wrist_roll", "gripper"]

params = [
    "P_Coefficient", "I_Coefficient", "D_Coefficient",
    "Acceleration", "Goal_Velocity",
    "Max_Torque_Limit", "Torque_Limit",
    "Minimum_Startup_Force",
    "CW_Dead_Zone", "CCW_Dead_Zone",
    "Protection_Current", "Protective_Torque", "Protection_Time",
    "Overload_Torque",
]

def read_settings(bus, motor_names, params):
    settings = {}
    for name in motor_names:
        settings[name] = {}
        for param in params:
            settings[name][param] = int(bus.read(param, name))
    return settings

# 팔로워 읽기
print("=== Follower Arm ===")
follower_settings = read_settings(robot.robot.bus, motor_names, params)
for name, vals in follower_settings.items():
    print(f"{name}: {vals}")

with open("nexodim/robots/configs/so101_follower.json", "w") as f:
    json.dump(follower_settings, f, indent=2)
print("저장: so101_follower.json\n")

# 리더 읽기
print("=== Leader Arm ===")
leader_settings = read_settings(robot.leader.bus, motor_names, params)
for name, vals in leader_settings.items():
    print(f"{name}: {vals}")

with open("nexodim/robots/configs/so101_leader.json", "w") as f:
    json.dump(leader_settings, f, indent=2)
print("저장: so101_leader.json")

robot.disconnect()