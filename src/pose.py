"""Pose detection: finds body landmarks in a webcam frame using MediaPipe's Pose Landmarker."""

from pathlib import Path
import time

import cv2
import mediapipe as mp

# Build the path from this file's location instead of using "models/..." directly,
# so the model is found no matter which folder the program is started from.
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "pose_landmarker_full.task"
# OpenCV colors are in BGR order, not RGB.
BONE_COLOR = (0, 255, 0)  # green
JOINT_COLOR = (0, 0, 255)  # red
# Points the model is less than 50% sure it can see are skipped, so we don't draw
# limbs it is only guessing at (like the arm hidden on the far side of the body).
MIN_VISIBILITY = 0.5

class PoseDetector:
    """Wraps MediaPipe's Pose Landmarker so the rest of the app can just ask for landmarks."""

    def __init__(self, model_path=MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Pose model not found at {model_path}. See the Setup section of the README."
            )

        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
            # VIDEO mode reuses information from the previous frame to track the body,
            # which is faster and steadier than treating every frame as a brand-new photo.
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_poses=1,
        )
        self._landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)
        self._last_timestamp_ms = -1


    def detect(self, frame_bgr):
        """Detects the 33 body landmarks in the frame. None if no person is found."""
        # I have to convert the frame to RGB since OpenCV uses BGR by default, but MediaPipe expects RGB.
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format  = mp.ImageFormat.SRGB, data = frame_rgb)

        # In video mode the timestamp has to keep going up. Two fast frames can land in the
        # same millisecond, so if that happens I just bump the number up by 1.
        timestamp_ms = max(int(time.monotonic() * 1000), self._last_timestamp_ms + 1)
        self._last_timestamp_ms = timestamp_ms

        result = self._landmarker.detect_for_video(image, timestamp_ms)
        if not result.pose_landmarks:
            return None
        return result.pose_landmarks[0]

    def close(self):
        """Releases the model's memory when the app closes."""
        self._landmarker.close()


def draw_skeleton(frame, landmarks):
    """Draw the body's joints (dots) and the bones connecting them (lines) onto the frame."""
    height, width = frame.shape[:2]
    # Landmarks are fractions of the image size (0 to 1), so scale them up to pixels.
    points = [(int(landmark.x * width), int(landmark.y * height)) for landmark in landmarks]
    visible = [(landmark.visibility or 0.0) >= MIN_VISIBILITY for landmark in landmarks]

    for bone in mp.tasks.vision.PoseLandmarksConnections.POSE_LANDMARKS:
        if visible[bone.start] and visible[bone.end]:
            cv2.line(frame, points[bone.start], points[bone.end], BONE_COLOR, 2)

    for point, is_visible in zip(points, visible):
        if is_visible:
            cv2.circle(frame, point, 4, JOINT_COLOR, -1)  
   

