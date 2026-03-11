import cv2
import numpy as np
from config import BALL_RADIUS, BALL_COLOR


class Renderer:
    def draw_ball(self, frame, ball):
        cx, cy = int(ball.x), int(ball.y)

        # Shadow (subtle ellipse on the floor)
        h = frame.shape[0]
        shadow_y = h - 18
        shadow_scale = max(0.2, 1.0 - (shadow_y - cy) / h)
        shadow_rx = int(BALL_RADIUS * shadow_scale * 1.5)
        shadow_ry = int(BALL_RADIUS * shadow_scale * 0.4)
        overlay = frame.copy()
        cv2.ellipse(overlay, (cx, shadow_y), (shadow_rx, shadow_ry), 0, 0, 360, (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        # Main ball
        cv2.circle(frame, (cx, cy), BALL_RADIUS, BALL_COLOR, -1)

        # Specular highlight (3D look)
        highlight_x = cx - BALL_RADIUS // 3
        highlight_y = cy - BALL_RADIUS // 3
        cv2.circle(frame, (highlight_x, highlight_y), BALL_RADIUS // 4, (255, 255, 255), -1)
        # Softer secondary highlight
        cv2.circle(frame, (highlight_x + 2, highlight_y + 2), BALL_RADIUS // 6, (220, 240, 255), -1)

    def draw_trail(self, frame, trail_points):
        n = len(trail_points)
        for i, (tx, ty) in enumerate(trail_points):
            alpha = (i + 1) / n
            radius = max(2, int(BALL_RADIUS * alpha * 0.6))
            # Fade from dim to bright
            b = int(BALL_COLOR[0] * alpha)
            g = int(BALL_COLOR[1] * alpha)
            r = int(BALL_COLOR[2] * alpha)
            overlay = frame.copy()
            cv2.circle(overlay, (int(tx), int(ty)), radius, (b, g, r), -1)
            cv2.addWeighted(overlay, alpha * 0.5, frame, 1 - alpha * 0.5, 0, frame)

    def draw_ui(self, frame, score, exit_progress):
        h, w, _ = frame.shape

        # Score — top left
        score_text = f"Score: {score}"
        cv2.putText(
            frame, score_text,
            (20, 40),
            cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 0, 0), 4, cv2.LINE_AA,
        )
        cv2.putText(
            frame, score_text,
            (20, 40),
            cv2.FONT_HERSHEY_DUPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA,
        )

        # Hint at bottom
        hint = "Juggle with your hands | Peace sign to exit"
        text_size = cv2.getTextSize(hint, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        hint_x = (w - text_size[0]) // 2
        cv2.putText(
            frame, hint,
            (hint_x, h - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3, cv2.LINE_AA,
        )
        cv2.putText(
            frame, hint,
            (hint_x, h - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA,
        )

    def flip(self, frame):
        return cv2.flip(frame, 1)
