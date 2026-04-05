import glob
import time
from lerobot.robots.so_follower import SOFollower
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.teleoperators.so_leader import SOLeader
from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig
from nexodim.base import NexodimRobot

class SO101(NexodimRobot):
    
    def __init__(self, id="default"):
        self.id = id
        self.robot = None
        self.leader = None

    def _find_port(self, name):
        input(f"{name} USB를 제거해주세요. 제거 후 엔터")
        before = set(glob.glob("/dev/ttyACM*"))
        input(f"{name} USB를 다시 꽂아주세요. 꽂은 후 엔터")
        time.sleep(3)
        after = set(glob.glob("/dev/ttyACM*"))
        new_port = list(after - before)[0]
        print(f"{name} 포트: {new_port}\n")
        return new_port

    def connect(self, mode="auto"):
        # 팔로워 연결
        follower_port = self._find_port(f"[{self.id}] Follower Arm")
        config = SOFollowerRobotConfig(
            port=follower_port,
            id=f"my_awesome_follower_arm"
        )
        self.robot = SOFollower(config)
        self.robot.connect(calibrate=False)

        # teach 모드면 리더도 연결
        if mode == "teach":
            leader_port = self._find_port(f"[{self.id}] Leader Arm")
            leader_config = SOLeaderTeleopConfig(
                port=leader_port,
                id="my_awesome_leader_arm"
            )
            self.leader = SOLeader(leader_config)
            self.leader.connect(calibrate=False)

        print(f"[{self.id}] SO101 연결 완료! (mode={mode})")

    def get_observation(self):
        return self.robot.get_observation()

    def send_action(self, action):
        return self.robot.send_action(action)

    def teleop(self):
        if self.leader is None:
            print("텔레옵 하려면 connect(mode='teach') 로 연결해야 해요!")
            return
        print(f"[{self.id}] 텔레옵 시작! 종료하려면 Ctrl+C")
        try:
            while True:
                action = self.leader.get_action()
                self.robot.send_action(action)
                time.sleep(1/60)
        except KeyboardInterrupt:
            print(f"[{self.id}] 텔레옵 종료")

    def disconnect(self):
        self.robot.disconnect()
        if self.leader:
            self.leader.disconnect()