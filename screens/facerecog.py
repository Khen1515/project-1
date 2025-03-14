import cv2
import os
import numpy as np
import threading
import platform
import random
import pygame  # For playing audio without FFmpeg
from gtts import gTTS  # Google Text-to-Speech
import mediapipe as mp

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivy.metrics import dp
from .CameraManager import CameraManager  # Shared Camera Manager
import hashlib
import os
import platform
import hashlib
from gtts import gTTS
from kivy.core.audio import SoundLoader

# Ensure "audio" folder exists
AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Detect OS
IS_ANDROID = "android" in platform.system().lower()

if IS_ANDROID:
    from plyer import tts  # Android TTS

    def speak(text):
        """Use Android TTS if running on an Android device."""
        try:
            tts.speak(text)
        except Exception as e:
            print(f"⚠️ TTS error: {e}")

else:
    def speak(text):
        """Use gTTS on non-Android devices, storing files in 'audio' folder."""
        try:
            filename = os.path.join(AUDIO_DIR, f"audio_{hashlib.sha256(text.encode()).hexdigest()[:10]}.mp3")

            if not os.path.exists(filename):  # Avoid redundant re-generation
                tts = gTTS(text=text, lang="tl")
                tts.save(filename)

            # Load and play the sound using Kivy's SoundLoader
            sound = SoundLoader.load(filename)
            if sound:
                sound.play()
                
                # Wait until the sound finishes playing
                while sound.state == "play":
                    pass

            os.remove(filename)  # Cleanup after playing
        except Exception as e:
            print(f"⚠️ gTTS error: {e}")

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detector = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# Load Face Recognition Model
try:
    recognizer = cv2.face.EigenFaceRecognizer_create()
except AttributeError:
    recognizer = cv2.face.FisherFaceRecognizer_create()

if os.path.exists("trained_faces.xml"):
    recognizer.read("trained_faces.xml")

# Load known faces

def load_known_faces(folder_path):
    label_map = {}
    label_index = 0
    for file_name in os.listdir(folder_path):
        if file_name.endswith(('.jpg', '.jpeg', '.png')):
            name = os.path.splitext(file_name)[0]
            label_map[label_index] = name
            label_index += 1
    return label_map

known_faces = load_known_faces("images/userfacialimage")

class FaceRecogScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = None
        self.is_scanning = False

        # UI Layout
        main_layout = MDBoxLayout(orientation='vertical')

        # Top bar
        top_bar = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56))
        back_button = MDIconButton(icon="arrow-left", pos_hint={"center_y": 0.5}, on_release=self.go_back)
        title_label = MDLabel(text="Face Recognition", halign="center", valign="center", font_style="H6")
        top_bar.add_widget(back_button)
        top_bar.add_widget(title_label)
        main_layout.add_widget(top_bar)

        # Body layout
        body_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.status_label = MDLabel(text="Initializing face recognition...", halign="center", size_hint=(1, None), height="40dp")
        self.image_widget = Image()
        self.scan_button = MDRaisedButton(text="Scan Face", pos_hint={"center_x": 0.5}, on_release=self.start_scan)

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

        self.status_label.text = "Scanning for faces..."
        self.is_scanning = True
        Clock.schedule_interval(self.update_video_feed, 1.0 / 30.0)
        threading.Thread(target=self.scan_faces, daemon=True).start()

    def scan_faces(self):
        while self.is_scanning:
            if not self.camera:
                return
            ret, frame = self.camera.get_frame()
            if ret:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detector.process(rgb_frame)
                if not results.detections:
                    continue
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    frame_h, frame_w, _ = frame.shape
                    x, y, w, h = int(bboxC.xmin * frame_w), int(bboxC.ymin * frame_h), int(bboxC.width * frame_w), int(bboxC.height * frame_h)
                    x, y, w, h = max(0, x), max(0, y), min(w, frame_w - x), min(h, frame_h - y)
                    face = rgb_frame[y:y + h, x:x + w]
                    if face.shape[0] > 20 and face.shape[1] > 20:
                        face = self.preprocess_face(face)
                        if face is not None:
                            label, confidence = recognizer.predict(face)
                            if confidence < 5000:
                                name = known_faces.get(label, "Unknown")
                                Clock.schedule_once(lambda dt: self.successful_scan(name))

    def preprocess_face(self, face):
        face = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY)
        face = cv2.resize(face, (200, 200))
        return face

    def successful_scan(self, name):
        self.is_scanning = False
        self.status_label.text = f"Recognized: {name}"
        greeting = f"This is, {name}" if name != "Unknown" else "Not Recognized"
        threading.Thread(target=speak, args=(greeting,), daemon=True).start()
        Clock.unschedule(self.update_video_feed)
        self.release_camera()

    def update_video_feed(self, dt):
        if not self.is_scanning or not self.camera:
            return
        ret, frame = self.camera.get_frame()
        if ret:
            buffer = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
            texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
            self.image_widget.texture = texture

    def release_camera(self):
        if self.camera:
            self.camera.release_camera()
            self.camera = None
