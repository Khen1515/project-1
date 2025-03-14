import cv2
import numpy as np
import threading
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from ultralytics import YOLO
from .CameraManager import CameraManager  # Import CameraManager
from kivy.uix.image import Image

# Load YOLOv8 Model
MODEL_PATH = "yolov8n.pt"
model = YOLO(MODEL_PATH)

class ObjectRecogScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = None
        self.is_scanning = False

        # UI Layout
        main_layout = MDBoxLayout(orientation='vertical')

        # Top bar
        top_bar = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56))
        back_button = MDIconButton(icon="arrow-left", pos_hint={"center_y": 0.5}, on_release=self.go_back)
        title_label = MDLabel(text="Object Recognition", halign="center", valign="center", font_style="H6")
        top_bar.add_widget(back_button)
        top_bar.add_widget(title_label)
        main_layout.add_widget(top_bar)

        # Body layout
        body_layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        self.status_label = MDLabel(text="Initializing object recognition...", halign="center", size_hint=(1, None), height="40dp")
        self.image_widget = Image()
        self.scan_button = MDRaisedButton(text="Scan Object", size_hint=(None, None), size=("150dp", "50dp"), pos_hint={"center_x": 0.5}, on_release=self.start_scan)

        body_layout.add_widget(self.status_label)
        body_layout.add_widget(self.image_widget)
        body_layout.add_widget(self.scan_button)
        main_layout.add_widget(body_layout)
        self.add_widget(main_layout)

    def go_back(self, *args):
        MDApp.get_running_app().sm.current = "dashboard"

    def on_enter(self):
        if not self.camera:
            self.camera = CameraManager()
        if not self.is_scanning:
            self.start_scan(None)

    def start_scan(self, instance):
        if not self.camera:
            self.camera = CameraManager()
        if self.is_scanning:
            return
        self.status_label.text = "Scanning for objects..."
        self.is_scanning = True
        Clock.schedule_interval(self.update_video_feed, 1.0 / 30.0)
        threading.Thread(target=self.detect_objects, daemon=True).start()

    def detect_objects(self):
        while self.is_scanning:
            if not self.camera:
                return
            ret, frame = self.camera.get_frame()
            if ret:
                results = model(frame)
                detections = results[0].boxes.data.cpu().numpy()
                for detection in detections:
                    x1, y1, x2, y2, conf, cls = map(int, detection[:6])
                    label = f"{model.names[cls]}: {conf:.2f}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                detected_objects = [model.names[int(d[5])] for d in detections]
                if detected_objects:
                    self.status_label.text = f"Detected: {', '.join(set(detected_objects))}"
                else:
                    self.status_label.text = "No objects detected"

    def update_video_feed(self, dt):
        if not self.is_scanning or not self.camera:
            return
        ret, frame = self.camera.get_frame()
        if ret:
            buffer = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
            texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
            self.image_widget.texture = texture
        else:
            print("⚠️ Failed to read frame from camera. Restarting...")
            self.release_camera()
            self.camera = CameraManager()
            Clock.schedule_once(lambda dt: self.start_scan(None), 1)

    def release_camera(self):
        if self.camera:
            self.camera.release_camera()
            self.camera = None

    def on_leave(self, *args):
        self.is_scanning = False
        Clock.unschedule(self.update_video_feed)
        self.release_camera()
