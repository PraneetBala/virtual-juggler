import cv2
from config import EXIT_GESTURE_FRAMES

# (tip_id, pip_id) pairs for each finger
EXTENDED_FINGERS = [(8, 6), (12, 10)]   # index + middle must be UP
CURLED_FINGERS  = [(16, 14), (20, 18)]  # ring + pinky must be DOWN


class GestureDetector:
    def __init__(self):
        self._counter = 0

    def is_peace_sign(self, hand_landmarks):
        # Index and middle fingers extended (tip y < pip y)
        for tip_id, pip_id in EXTENDED_FINGERS:
            if hand_landmarks[tip_id][1] >= hand_landmarks[pip_id][1]:
                return False
        # Ring and pinky curled (tip y > pip y)
        for tip_id, pip_id in CURLED_FINGERS:
            if hand_landmarks[tip_id][1] <= hand_landmarks[pip_id][1]:
                return False
        return True

    def check_exit(self, hands_list, frame_shape, frame):
        peace_detected = any(self.is_peace_sign(hand) for hand in hands_list)

        if peace_detected:
            self._counter += 1
        else:
            self._counter = max(0, self._counter - 2)  # decay faster than growth

        self._draw_progress(frame, self._counter)

        return self._counter >= EXIT_GESTURE_FRAMES

    @property
    def exit_progress(self):
        return min(self._counter / EXIT_GESTURE_FRAMES, 1.0)

    def _draw_progress(self, frame, counter):
        if counter <= 0:
            return

        h, w, _ = frame.shape
        progress = min(counter / EXIT_GESTURE_FRAMES, 1.0)

        bar_width = 200
        bar_height = 20
        x = w - bar_width - 20
        y = 20

        # Background bar
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (50, 50, 50), -1)
        # Filled portion
        filled_w = int(bar_width * progress)
        color = (0, int(255 * progress), int(255 * (1 - progress)))
        cv2.rectangle(frame, (x, y), (x + filled_w, y + bar_height), color, -1)
        # Border
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (200, 200, 200), 1)

        label = "Peace sign to exit"
        cv2.putText(
            frame, label,
            (x, y - 6),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA,
        )
