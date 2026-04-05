import glob
import time
import json
import os
import cv2
from lerobot.robots.so_follower import SOFollower
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.teleoperators.so_leader import SOLeader
from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig
from nexodim.base import NexodimRobot


class SO101(NexodimRobot):

    def __init__(self, id="default", camera_index=None):
        self.id = id
        self.camera_index = camera_index
        self.robot = None
        self.leader = None
        self.camera = None
        self.robot_port = None
        self.leader_port = None

    # ── 내부 유틸 ──

    def _find_port(self, name):
        input(f"[{self.id}] {name} USB를 제거해주세요. 제거 후 엔터")
        before = set(glob.glob("/dev/ttyACM*"))
        input(f"[{self.id}] {name} USB를 다시 꽂아주세요. 꽂은 후 엔터")
        time.sleep(3)
        after = set(glob.glob("/dev/ttyACM*"))
        new_port = list(after - before)[0]
        print(f"[{self.id}] {name} 포트: {new_port}\n")
        return new_port

    def _find_camera(self):
        input(f"[{self.id}] 카메라 USB를 제거해주세요. 제거 후 엔터")
        before = set(glob.glob("/dev/video*"))
        input(f"[{self.id}] 카메라 USB를 다시 꽂아주세요. 꽂은 후 엔터")
        time.sleep(3)
        after = set(glob.glob("/dev/video*"))
        new_devices = sorted(after - before)
        index = int(new_devices[0].replace("/dev/video", ""))
        print(f"[{self.id}] 카메라 인덱스: {index}\n")
        return index

    def _connect_follower(self, calibrate=False):
        if not self.robot_port:
            self.robot_port = self._find_port("Follower Arm")
        config = SOFollowerRobotConfig(
            port=self.robot_port,
            id="my_awesome_follower_arm"
        )
        self.robot = SOFollower(config)
        self.robot.connect(calibrate=calibrate)

    def _connect_leader(self, calibrate=False):
        if not self.leader_port:
            self.leader_port = self._find_port("Leader Arm")
        leader_config = SOLeaderTeleopConfig(
            port=self.leader_port,
            id="my_awesome_leader_arm"
        )
        self.leader = SOLeader(leader_config)
        self.leader.connect(calibrate=calibrate)

    # ── 메인 함수 ──

    def connect(self, mode="auto", use_camera=True):
        self._connect_follower(calibrate=False)

        if mode == "teach":
            self._connect_leader(calibrate=False)

        if use_camera:
            self.connect_camera()

        print(f"[{self.id}] SO101 연결 완료! (mode={mode})")

    def connect_camera(self, camera_index=None):
        if camera_index is not None:
            self.camera_index = camera_index
        elif self.camera_index is None:
            self.camera_index = self._find_camera()

        if self.camera:
            self.camera.release()
        self.camera = cv2.VideoCapture(self.camera_index)
        if self.camera.isOpened():
            print(f"[{self.id}] 카메라 연결 완료!")
        else:
            print(f"[{self.id}] 카메라 연결 실패.")
            self.camera = None

    def calibrate(self, target="all"):
        if target in ("follower", "all"):
            # 기존 연결 끊고 캘리브레이션 포함 재연결
            try:
                self.robot.disconnect()
            except:
                pass
            self._connect_follower(calibrate=True)
            print(f"[{self.id}] Follower 캘리브레이션 완료!")

        if target in ("leader", "all"):
            try:
                self.leader.disconnect()
            except:
                pass
            self._connect_leader(calibrate=True)
            print(f"[{self.id}] Leader 캘리브레이션 완료!")

    def setup(self):
        config_dir = os.path.join(os.path.dirname(__file__), "configs")

        with open(os.path.join(config_dir, "so101_follower.json"), "r") as f:
            settings = json.load(f)
        for motor_name, params in settings.items():
            for param, value in params.items():
                self.robot.bus.write(param, motor_name, value)
        print(f"[{self.id}] Follower 모터 세팅 적용 완료")

        if self.leader:
            with open(os.path.join(config_dir, "so101_leader.json"), "r") as f:
                settings = json.load(f)
            for motor_name, params in settings.items():
                for param, value in params.items():
                    self.leader.bus.write(param, motor_name, value)
            print(f"[{self.id}] Leader 모터 세팅 적용 완료")

    def first_setup(self):
        # 포트 찾기
        self.robot_port = self._find_port("Follower Arm")
        self.leader_port = self._find_port("Leader Arm")

        # 캘리브레이션 포함 연결
        self._connect_follower(calibrate=True)
        self._connect_leader(calibrate=True)

        # 모터 세팅 적용
        self.setup()

        print(f"[{self.id}] 초기 셋업 완료!")
        self.disconnect()

    # ── 관측/제어 ──

    def get_observation(self):
        obs = self.robot.get_observation()
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                obs["camera"] = frame
        return obs

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

    # ── 해제 ──

    def disconnect_leader(self):
        if self.leader:
            self.leader.disconnect()
            self.leader = None
            print(f"[{self.id}] Leader Arm 해제 완료")

    def disconnect_camera(self):
        if self.camera:
            self.camera.release()
            self.camera = None
            print(f"[{self.id}] Camera 해제 완료")

    def disconnect(self):
        if self.robot:
            self.robot.disconnect()
            print(f"[{self.id}] Main Robot 해제 완료")
        self.disconnect_leader()
        self.disconnect_camera()