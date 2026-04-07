"""
SmolVLA 실제 로봇 제어 테스트

이 스크립트는 SmolVLA 모델을 로드하고 SO101 로봇이
실제로 작업을 수행하도록 연속 추론 루프를 실행합니다.

사용법:
    python test_smolvla_run.py

주의:
    - 로봇 주변에 장애물이 없는지 확인하세요
    - 처음 실행 시 로봇이 예상치 못하게 움직일 수 있으니
      비상 정지(전원 차단)를 준비하세요
    - smolvla_base는 파인튜닝 전 베이스 모델이므로
      정확한 작업 수행은 어렵습니다. 동작 확인 용도입니다.
"""

import sys
import time
sys.path.append('/home/nyoung/dev/NxD/Zip0')
import nexodim as nxd


def main():
    # ── 설정 ──
    TASK = "pick up the cup"       # 작업 명령
    MAX_STEPS = 300                # 최대 추론 스텝 수
    FPS = 30                       # 제어 주파수
    MODEL_ID = "lerobot/smolvla_base"  # 모델 (파인튜닝 모델로 교체 가능)

    # ── 로봇 연결 ──
    robot = nxd.robots.SO101()
    robot.connect()
    print(f"\n로봇 연결 완료!")

    # ── 정책 로드 ──
    policy = nxd.policies.vla.SmolVLA()
    policy.load_policy(MODEL_ID, task=TASK)
    print(f"\n모델 로드 완료!")
    print(f"작업: '{TASK}'")
    print(f"최대 스텝: {MAX_STEPS}")
    print(f"FPS: {FPS}")

    # ── 실행 전 확인 ──
    print("\n" + "=" * 50)
    print("  로봇이 움직이기 시작합니다!")
    print("  - Ctrl+C 로 언제든 정지할 수 있습니다")
    print("  - 로봇 주변 안전을 확인하세요")
    print("=" * 50)
    input("\n준비되면 엔터를 누르세요...")

    # ── 추론 루프 실행 ──
    interval = 1.0 / FPS
    step = 0

    try:
        for step in range(MAX_STEPS):
            t_start = time.time()

            # 1. 관측
            obs = robot.get_observation()

            # 2. 추론
            action = policy.inference_policy(obs)

            # 3. 로봇에 액션 전달
            robot.send_action(action)

            # 로그 (10스텝마다)
            if step % 10 == 0:
                elapsed = time.time() - t_start
                actual_fps = 1.0 / max(elapsed, 1e-6)
                print(
                    f"  step {step:4d}/{MAX_STEPS}  |  "
                    f"fps: {actual_fps:5.1f}  |  "
                    f"gripper: {action.get('gripper.pos', 0):.2f}"
                )

            # FPS 유지
            elapsed = time.time() - t_start
            sleep_time = max(0, interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print(f"\n\n사용자 중단! (step={step})")

    # ── 종료 ──
    print("\n로봇 정지 중...")
    robot.disconnect()
    print("완료!")


if __name__ == "__main__":
    main()