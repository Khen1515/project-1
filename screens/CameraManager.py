import cv2
import numpy as np

class CameraManager:
    _instance = None  # Singleton instance

    def __new__(cls, video_source=0):
        if cls._instance is None:
            cls._instance = super(CameraManager, cls).__new__(cls)
            cls._instance.video_source = video_source
            cls._instance.capture = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)  # ✅ Use DirectShow for better Windows compatibility

            # ✅ Set High-Quality Resolution
            cls._instance.set_resolution(1280, 720)  # Change to (1920, 1080) if needed

            if not cls._instance.capture.isOpened():
                print("⚠️ Error: Could not access the camera.")
        
        return cls._instance

    def set_resolution(self, width, height):
        """✅ Set camera resolution to improve quality."""
        if self.capture and self.capture.isOpened():
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            print(f"📷 Camera resolution set to {width}x{height}")

    def get_frame(self, preprocess=False):
        """Retrieve a frame from the camera with optimized settings. If preprocess=True, convert to grayscale."""
        if not self.capture or not self.capture.isOpened():
            print("⚠️ Error: Attempted to read from a closed camera.")
            return False, None  # ✅ Prevent crash if the camera is closed

        ret, frame = self.capture.read()

        # ✅ Ensure the frame is valid before processing
        if not ret or frame is None:
            print("⚠️ Error: Camera did not return a valid frame.")
            return False, None

        frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)  # ✅ Smooth downscaling
        if preprocess:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # ✅ Convert to grayscale for OCR
        return ret, frame


    def release_camera(self):
        """Release the camera."""
        if self.capture and self.capture.isOpened():
            self.capture.release()
            CameraManager._instance = None  # Reset singleton instance
