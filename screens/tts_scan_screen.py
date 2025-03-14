import cv2
import easyocr
import numpy as np
import threading
import os
import random
import re
import platform
from gtts import gTTS
import hashlib
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.core.audio import SoundLoader  # Use Kivy's SoundLoader
from .CameraManager import CameraManager  # Use OpenCV CameraManager

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

            sound = SoundLoader.load(filename)
            if sound:
                sound.play()
                while sound.state == "play":
                    pass  # Wait until the sound finishes playing

            os.remove(filename)  # Cleanup after playing
        except Exception as e:
            print(f"⚠️ gTTS error: {e}")


class TTSScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = None  # Use OpenCV-based CameraManager
        self.is_scanning = False
        self.ocr_result = "Position object in front of the camera"
        self.reader = easyocr.Reader(['en', 'tl'])

        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Top bar
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56))
        back_button = MDIconButton(icon="arrow-left", pos_hint={"center_y": 0.5}, on_release=self.go_back)
        title_label = MDLabel(text="TTS Scan", halign="center", valign="center", font_style="H6")
        top_bar.add_widget(back_button)
        top_bar.add_widget(title_label)
        main_layout.add_widget(top_bar)

        # Camera Feed
        self.image_widget = Image()
        main_layout.add_widget(self.image_widget)

        # OCR Text Display
        scroll_view = ScrollView(size_hint=(1, 0.3))
        self.text_area = TextInput(
            text=self.ocr_result,
            readonly=True,
            size_hint_y=None,
            height=150,
            background_color=(0.9, 0.9, 0.9, 1),
            foreground_color=(0, 0, 0, 1),
        )
        scroll_view.add_widget(self.text_area)
        main_layout.add_widget(scroll_view)

        # Buttons layout
        btn_box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, None), height="50dp")
        self.scan_button = MDRaisedButton(text="Start Scanning", size_hint=(1, 1), on_release=self.toggle_scan)
        self.photo_button = MDRaisedButton(text="Take Photo", size_hint=(1, 1), on_release=self.capture_photo)
        self.tts_button = MDRaisedButton(text="Read Aloud", size_hint=(1, 1), on_release=self.read_aloud)

        btn_box.add_widget(self.scan_button)
        btn_box.add_widget(self.photo_button)
        btn_box.add_widget(self.tts_button)

        main_layout.add_widget(btn_box)
        self.add_widget(main_layout)

    def go_back(self, *args):
        MDApp.get_running_app().sm.current = "dashboard"

    def on_pre_enter(self, *args):
        if not self.camera:
            print("📷 Initializing OpenCV CameraManager...")
            self.camera = CameraManager()
        Clock.schedule_interval(self.update_camera_feed, 1.0 / 30.0)
        
    def on_pre_leave(self, *args):
        Clock.unschedule(self.update_camera_feed)
        if self.camera:
            self.camera.release_camera()
            self.camera = None

    def update_camera_feed(self, dt):
        """Continuously update the video feed."""
        if not self.camera:
            return
        ret, frame = self.camera.get_frame()
        if ret:
            buffer = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
            texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
            self.image_widget.texture = texture

    def toggle_scan(self, *_):
        if self.is_scanning:
            self.stop_scan()
        else:
            self.start_scan()

    def start_scan(self):
        if not self.camera:
            self.camera = CameraManager()
        self.is_scanning = True
        self.scan_button.text = "Stop Scanning"
        threading.Thread(target=self.scan_text, daemon=True).start()
        self.scan_text()  # Start scanning immediately


    def stop_scan(self):
        self.is_scanning = False
        self.scan_button.text = "Start Scanning"


    def scan_text(self):
        while self.is_scanning:
            ret, frame = self.camera.get_frame()
            if not ret or frame is None:
                print("⚠️ Failed to capture frame. Restarting camera...")
                self.camera.release_camera()
                self.camera = CameraManager()
                return

            preprocessed = self.preprocess_image(frame)
            results = self.reader.readtext(preprocessed)

            detected_text = []
            for res in results:
                text, confidence = res[1], res[2]
                if confidence >= 0.8:  # ✅ Only keep high-confidence text
                    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)  # Remove special characters
                    detected_text.append(text)

            final_text = " ".join(detected_text)

            if final_text.strip():
                Clock.schedule_once(lambda dt: self.update_text_display(final_text))
                threading.Thread(target=speak, args=(final_text,), daemon=True).start()
                Clock.schedule_once(lambda dt: self.stop_scan(), 0.5)
                return

            Clock.schedule_once(lambda dt: self.retry_scan(), 2)



    def retry_scan(self):
        if self.is_scanning:
            threading.Thread(target=self.scan_text, daemon=True).start()

    def preprocess_image(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.resize(gray, (640, 480))

    def capture_photo(self, *_):
        if not self.camera:
            self.camera = CameraManager()
        ret, frame = self.camera.get_frame()
        if not ret or frame is None:
            print("❌ Failed to capture photo.")
            return

        preprocessed = self.preprocess_image(frame)
        results = self.reader.readtext(preprocessed)

        detected_text = []
        for res in results:
            text, confidence = res[1], res[2]
            if confidence >= 0.8:  # ✅ Apply the same confidence threshold
                text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
                detected_text.append(text)

        final_text = " ".join(detected_text)

        if final_text.strip():
            Clock.schedule_once(lambda dt: self.update_text_display(final_text))
            threading.Thread(target=speak, args=(final_text,), daemon=True).start()
            Clock.schedule_once(lambda dt: self.stop_scan(), 0.5)  
        else:
            message = "No text detected. Try again."
            Clock.schedule_once(lambda dt: self.update_text_display(message))
            threading.Thread(target=speak, args=(message,), daemon=True).start()



    def read_aloud(self, *_):
        threading.Thread(target=speak, args=(self.ocr_result,), daemon=True).start()

    def update_text_display(self, text):
        self.ocr_result = text
        self.text_area.text = text
