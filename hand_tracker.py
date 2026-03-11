import os
import urllib.request
import mediapipe as mp
import cv2

FINGERTIP_IDS = [4, 8, 12, 16, 20]

MODEL_PATH = "hand_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)

# Connections to draw (landmark index pairs)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),           # index
    (0, 9), (9, 10), (10, 11), (11, 12),      # middle
    (0, 13), (13, 14), (14, 15), (15, 16),    # ring
    (0, 17), (17, 18), (18, 19), (19, 20),    # pinky
    (5, 9), (9, 13), (13, 17), (0, 17),       # palm
]


class HandTracker:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            print("Downloading hand landmarker model (~10 MB)...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("Model downloaded.")

        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = HandLandmarker.create_from_options(options)

    def process(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.landmarker.detect(mp_image)

        hands_list = []
        if result.hand_landmarks:
            for hand_lms in result.hand_landmarks:
                landmark_dict = {
                    idx: (int(lm.x * w), int(lm.y * h))
                    for idx, lm in enumerate(hand_lms)
                }
                hands_list.append(landmark_dict)
                self._draw_landmarks(frame, landmark_dict)

        return hands_list

    def _draw_landmarks(self, frame, landmark_dict):
        for start, end in HAND_CONNECTIONS:
            if start in landmark_dict and end in landmark_dict:
                cv2.line(frame, landmark_dict[start], landmark_dict[end], (80, 200, 80), 2)
        for idx, (x, y) in landmark_dict.items():
            if idx in FINGERTIP_IDS:
                cv2.circle(frame, (x, y), 6, (255, 255, 255), -1)
                cv2.circle(frame, (x, y), 6, (0, 150, 255), 2)
            else:
                cv2.circle(frame, (x, y), 4, (200, 200, 200), -1)

    def get_fingertips(self, hand_landmarks):
        return [hand_landmarks[tip_id] for tip_id in FINGERTIP_IDS]

    def get_palm_center(self, hand_landmarks):
        return hand_landmarks[0]
