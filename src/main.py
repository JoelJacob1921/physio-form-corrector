"""Entry point: opens the webcam and shows the live feed in a window."""

import sys
import time

import cv2
from pose import PoseDetector, draw_skeleton


CAMERA_INDEX = 0
WINDOW_NAME = "Physio Form Corrector"
QUIT_KEY = "q"
MAX_FAILED_READS = 30
RETRY_DELAY_SECONDS = 0.1
TEXT_COLOR = (0, 0, 255)  
# red (OpenCV uses BGR, so red comes last)


def open_camera(index):
    """Open the webcam at the given index, or exit with a helpful message if it can't."""
    camera = cv2.VideoCapture(index)
    if not camera.isOpened():
        # On the first run, macOS shows a camera-permission prompt. If it's denied,
        # OpenCV doesn't say what went wrong, so we explain the likely cause ourselves.
        print(
            f"Could not open camera {index}. Check that no other application is using it, and that "
            "your terminal/VS Code has camera access in System Settings -> Privacy & Security -> Camera."
        )
        # Exit code 1 means "ended because of an error"; 0 would mean success.
        sys.exit(1)
    return camera


def main():
    camera = open_camera(CAMERA_INDEX)
    try:
        detector = PoseDetector()
    except FileNotFoundError as error:
        # If the model file is missing there's nothing useful we can do, so we hand the
        # camera back and show our "here's how to fix it" message instead of a weird error.
        camera.release()
        print(error)
        sys.exit(1)

    failed_reads = 0
    while True:
        frame_ok, frame = camera.read()
        if not frame_ok:
            # macOS cameras return empty frames instantly while warming up, so we
            # pause between retries and only give up after ~3 seconds of failures.
            failed_reads += 1
            if failed_reads >= MAX_FAILED_READS:
                print("Lost the camera feed. Exiting.")
                break
            time.sleep(RETRY_DELAY_SECONDS)
            continue
        failed_reads = 0

        # Mirror the image so it behaves like a mirror for the user, which feels more natural.
        frame = cv2.flip(frame, 1)
        landmarks = detector.detect(frame)
        if landmarks is None:
            # Nobody's in view (or it's too dark to tell), so it say so on screen
            # instead of leaving the user wondering why nothing is happening.
            cv2.putText(frame, "No person detected", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, TEXT_COLOR, 2)
        else:
            draw_skeleton(frame, landmarks)

        cv2.imshow(WINDOW_NAME, frame)

        # waitKey also gives OpenCV time to redraw the window; without it the window stays blank.
        if cv2.waitKey(1) & 0xFF == ord(QUIT_KEY):
            break

    camera.release()
    cv2.destroyAllWindows()
    detector.close()


# Only run main() when this file is run directly, so importing it elsewhere won't start the webcam.
if __name__ == "__main__":
    main()
