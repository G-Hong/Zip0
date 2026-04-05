from abc import ABC, abstractmethod

class NexodimRobot(ABC):
    """NxD 표준 규격 - 모든 로봇은 이걸 따라야 함"""

    @abstractmethod
    def connect(self):
        """로봇 연결"""
        pass

    @abstractmethod
    def get_observation(self):
        """현재 상태 읽기"""
        pass

    @abstractmethod
    def send_action(self, action):
        """로봇 움직이기"""
        pass

    @abstractmethod
    def disconnect(self):
        """연결 해제"""
        pass