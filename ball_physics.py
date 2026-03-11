import math
from config import GRAVITY, BOUNCE_DAMPING, HIT_DISTANCE, HIT_VELOCITY

# Max horizontal speed injected by palm tilt
MAX_TILT_VX = 14.0
# How much palm swing velocity blends into the hit
PALM_VELOCITY_BLEND = 0.4
# Max speed multiplier from fast upward swing
MAX_SPEED_SCALE = 2.0


class Ball:
    def __init__(self, frame_width, frame_height):
        self.x = frame_width // 2
        self.y = frame_height // 4
        self.vx = 0.0
        self.vy = 0.0
        self._prev_fingertips = {}   # index → (x, y)
        self._prev_palm_center = {}  # hand_idx → (x, y)
        self._hit_cooldown = 0

    def update(self, frame_width, frame_height):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        # Floor
        if self.y >= frame_height - 20:
            self.y = frame_height - 20
            self.vy = -abs(self.vy) * BOUNCE_DAMPING
            self.vx *= BOUNCE_DAMPING

        # Ceiling
        if self.y <= 20:
            self.y = 20
            self.vy = abs(self.vy) * BOUNCE_DAMPING

        # Walls
        if self.x <= 20:
            self.x = 20
            self.vx = abs(self.vx) * BOUNCE_DAMPING
        elif self.x >= frame_width - 20:
            self.x = frame_width - 20
            self.vx = -abs(self.vx) * BOUNCE_DAMPING

        self.vx *= 0.99

        if self._hit_cooldown > 0:
            self._hit_cooldown -= 1

    def apply_hit(self, fingertip_positions, hands_data=None):
        """
        fingertip_positions: flat list of (x, y) for all fingertips across all hands.
        hands_data: list of landmark dicts (full hand, one per hand).
        Returns True if a hit was registered.
        """
        if self._hit_cooldown > 0:
            self._prev_fingertips = {i: pos for i, pos in enumerate(fingertip_positions)}
            self._update_palm_history(hands_data)
            return False

        hit = False
        for i, (fx, fy) in enumerate(fingertip_positions):
            dist = math.hypot(fx - self.x, fy - self.y)
            if dist < HIT_DISTANCE:
                prev = self._prev_fingertips.get(i)
                if prev is not None and fy < prev[1]:  # fingertip moving upward
                    tip_dy = prev[1] - fy  # pixels moved up this frame
                    self.vx, self.vy = self._compute_velocity(
                        tip_dy, i, hands_data
                    )
                    self._hit_cooldown = 15
                    hit = True
                    break

        self._prev_fingertips = {i: pos for i, pos in enumerate(fingertip_positions)}
        self._update_palm_history(hands_data)
        return hit

    def _compute_velocity(self, tip_dy, tip_idx, hands_data):
        # Scale vy by how fast the fingertip is moving upward (capped)
        speed_scale = min(tip_dy / 8.0, MAX_SPEED_SCALE)
        speed_scale = max(speed_scale, 1.0)
        vy = HIT_VELOCITY * speed_scale

        # Horizontal component from palm tilt + palm swing velocity
        vx = 0.0
        if hands_data:
            # Find the hand whose fingertip triggered the hit
            # Each hand contributes 5 fingertips in order; derive hand index
            hand_idx = tip_idx // 5
            hand_idx = min(hand_idx, len(hands_data) - 1)
            hand = hands_data[hand_idx]

            wrist = hand.get(0)
            mcp9 = hand.get(9)   # middle finger MCP — palm orientation anchor

            if wrist and mcp9:
                palm_dx = mcp9[0] - wrist[0]
                palm_dy = mcp9[1] - wrist[1]
                palm_len = math.hypot(palm_dx, palm_dy)
                if palm_len > 0:
                    # Normalized horizontal tilt: -1 (left) → +1 (right)
                    tilt = palm_dx / palm_len
                    vx = tilt * MAX_TILT_VX

                # Add palm swing velocity (how fast the palm itself is moving)
                prev_palm = self._prev_palm_center.get(hand_idx)
                curr_palm = wrist
                if prev_palm is not None:
                    palm_vx = curr_palm[0] - prev_palm[0]
                    palm_vy = curr_palm[1] - prev_palm[1]
                    vx += palm_vx * PALM_VELOCITY_BLEND
                    # Upward palm swing boosts the hit
                    if palm_vy < 0:
                        extra = abs(palm_vy) * PALM_VELOCITY_BLEND
                        vy -= extra  # vy is negative (upward), make it more negative

        return vx, vy

    def _update_palm_history(self, hands_data):
        if hands_data:
            for i, hand in enumerate(hands_data):
                wrist = hand.get(0)
                if wrist:
                    self._prev_palm_center[i] = wrist
