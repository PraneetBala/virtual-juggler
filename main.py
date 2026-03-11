import cv2
from collections import deque

from config import CAMERA_INDEX
from hand_tracker import HandTracker
from ball_physics import Ball
from gesture_detector import GestureDetector
from renderer import Renderer


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Read one frame to get dimensions
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read from camera.")
        cap.release()
        return

    frame_h, frame_w, _ = frame.shape

    tracker = HandTracker()
    ball = Ball(frame_w, frame_h)
    gesture = GestureDetector()
    renderer = Renderer()

    trail = deque(maxlen=10)
    score = 0

    print("Virtual Juggler started! Juggle with your hands.")
    print("Peace sign to exit, or press 'q'.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror frame so it feels like a mirror
        frame = renderer.flip(frame)

        # Track hands
        hands_list = tracker.process(frame)

        # Collect all fingertip positions from all detected hands
        all_fingertips = []
        for hand in hands_list:
            all_fingertips.extend(tracker.get_fingertips(hand))

        # Check for hits and update score
        if ball.apply_hit(all_fingertips, hands_list):
            score += 1

        # Update ball physics
        ball.update(frame_w, frame_h)

        # Update trail
        trail.append((ball.x, ball.y))

        # Check exit gesture
        if gesture.check_exit(hands_list, frame.shape, frame):
            print("Exit gesture detected. Bye!")
            break

        # Render
        renderer.draw_trail(frame, trail)
        renderer.draw_ball(frame, ball)
        renderer.draw_ui(frame, score, gesture.exit_progress)

        cv2.imshow("Virtual Juggler", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Final score: {score}")


if __name__ == "__main__":
    main()
