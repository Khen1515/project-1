import os
import threading
import time
import cv2
import numpy as np
import hashlib
import speech_recognition as sr
from gtts import gTTS
import mediapipe as mp
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp  # Import directly to avoid circular imports
from kivy.core.audio import SoundLoader  # Use Kivy's SoundLoader instead of pygame
from .CameraManager import CameraManager  # Shared Camera Manager


def recognize_speech():
    """Uses the microphone to recognize speech and return the detected text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening for voice command...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            command = recognizer.recognize_google(audio, language="tl-PH")
            print(f"🔊 Recognized: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            return "no speech"
        except sr.UnknownValueError:
            return "error"
        except sr.RequestError:
            return "error"

def speak(text):
    """Convert text to speech and play it using Kivy's SoundLoader."""
    filename = f"audio_{hashlib.sha256(text.encode()).hexdigest()[:10]}.mp3"

    if not os.path.exists(filename):
        tts = gTTS(text=text, lang="tl")
        tts.save(filename)

    sound = SoundLoader.load(filename)
    if sound:
        sound.play()
        while sound.state == "play":
            pass  # Wait until the sound finishes playing

    os.remove(filename)  # Cleanup after playing



user_login_kv = """
<UserLoginScreen>:
    name: "user_login"
    MDFloatLayout:
        Image:
            id: bg_image
            source: ""
            allow_stretch: True
            keep_ratio: False
            size_hint: 1, 1

        Image:
            source: "images/newto.png"
            size_hint: None, None
            size: dp(200), dp(200)
            pos_hint: {"center_x": 0.5, "top": 0.95}

        MDLabel:
            text: "User Login"
            font_style: "H5"
            halign: "center"
            pos_hint: {"center_x": 0.5, "center_y": 0.65}

        MDTextField:
            id: user_username
            hint_text: "Username"
            pos_hint: {"center_x": 0.5, "center_y": 0.50}
            size_hint_x: 0.8
            on_text: app.root.get_screen("user_login").announce_character(self, self.text)
            on_focus: app.root.get_screen("user_login").announce_input(self, self.focus)

        FloatLayout:
            size_hint: 0.8, None
            height: dp(50)
            pos_hint: {"center_x": 0.5, "center_y": 0.39}

            MDTextField:
                id: user_password
                hint_text: "Password"
                password: True
                size_hint_x: 1
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                on_text: app.root.get_screen("user_login").announce_character(self, self.text)
                on_focus: app.root.get_screen("user_login").announce_input(self, self.focus)

            MDIconButton:
                id: show_password_btn
                icon: "eye-off"
                size_hint: None, None
                size: dp(40), dp(40)
                pos_hint: {"center_y": 0.5}
                x: user_password.right - self.width - dp(5)
                on_release:
                    user_password.password = not user_password.password
                    self.icon = "eye" if not user_password.password else "eye-off"

        MDRaisedButton:
            text: "Sign In"
            size_hint_y: None
            height: dp(45)
            pos_hint: {"center_x": 0.5, "center_y": 0.25}
            on_release:
                app.sign_in_user()

        MDLabel:
            text: "or"
            halign: "center"
            font_style: "Body1"
            pos_hint: {"center_x": 0.5, "center_y": 0.18}

        MDRaisedButton:
            text: "Scan Faces"
            size_hint_y: None
            height: dp(45)
            pos_hint: {"center_x": 0.5, "center_y": 0.10}
            on_release:
                app.root.get_screen("user_login").start_scan()
"""

Builder.load_string(user_login_kv)


class UserLoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = None
        self.is_scanning = False
        self.recognizer_trained = False
        self.confidence_threshold = 5000

        # Initialize Face Detection with MediaPipe
        self.face_detector = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.5)

        # Initialize Face Recognizer safely
        self._initialize_recognizer()

        if self.recognizer is None:
            print("❌ No face recognizer available. Face recognition features will be disabled.")
        else:
            # Train & Load Faces Automatically on Startup
            self.load_known_faces()
            if os.path.exists("trained_faces.xml"):
                self.recognizer.read("trained_faces.xml")
                self.recognizer_trained = True

    def on_enter(self):
        """Announce login page and start voice recognition."""
        threading.Thread(target=speak, args=("Login Page. Enter details or use face recognition.",), daemon=True).start()
        threading.Thread(target=self.process_voice_command, daemon=True).start()

    def announce_input(self, instance, value):
        """Announce the field when focused."""
        if value:
            threading.Thread(target=speak, args=(instance.hint_text,), daemon=True).start()

    def announce_character(self, instance, value):
        """Announce each character as the user types."""
        if value:
            last_char = value[-1]
            if last_char.isalnum() or last_char in "!@#$%^&*()-_=+[]{};:'\",.<>?/|~":
                threading.Thread(target=speak, args=(last_char,), daemon=True).start()

    def process_voice_command(self):
        """Recognizes voice commands and navigates accordingly."""
        self.voice_recognition_active = True
        while self.voice_recognition_active:
            command = recognize_speech()
            if command in ["gamitin ang pagkilala sa mukha", "face recognition", "scan face", "scan"]:
                Clock.schedule_once(lambda dt: self.start_scan(), 0)
                break

    def load_known_faces(self, folder_path="images/userfacialimage"):
        """Load known faces and match them to Firebase user full names."""
        known_faces, labels = [], []
        self.label_map = {}  # Map label indices to full names

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for idx, file_name in enumerate(os.listdir(folder_path)):
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(folder_path, file_name)
                image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if image is None:
                    continue
                try:
                    image = cv2.resize(image, (200, 200))
                except Exception as e:
                    print("❌ Error resizing image:", e)
                    continue
                known_faces.append(image)
                labels.append(idx)
                full_name = os.path.splitext(file_name)[0]  # Extract name from filename
                self.label_map[idx] = full_name

        if known_faces and self.recognizer is not None:
            try:
                self.recognizer.train(known_faces, np.array(labels))
                self.recognizer.save("trained_faces.xml")
                self.recognizer_trained = True
                print(f"✅ Faces trained: {len(known_faces)}")
            except Exception as e:
                print("❌ Training failed:", e)
        else:
            print("⚠️ No faces found. Training skipped.")

    def start_scan(self):
        """Ensure training happens before scanning faces."""
        if not self.recognizer_trained:
            print("⚠️ No trained faces found. Training now...")
            self.load_known_faces()  # Train before scanning
            if not self.recognizer_trained:
                threading.Thread(target=speak, args=("No trained faces found!",), daemon=True).start()
                return

        if not self.camera:
            self.camera = CameraManager()

        self.is_scanning = True
        threading.Thread(target=self.recognize_face, daemon=True).start()

    def recognize_face(self):
        """Recognize a face and authenticate the user."""
        start_time = time.time()
        timeout = 30  # seconds timeout

        while self.is_scanning:
            if time.time() - start_time > timeout:
                print("⏰ Face scanning timed out.")
                threading.Thread(target=speak, args=("Face scanning timed out. Please try again.",), daemon=True).start()
                self.is_scanning = False
                return

            if not self.camera:
                return

            ret, frame = self.camera.get_frame()
            if not ret:
                continue

            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            except Exception as e:
                print("❌ Error converting frame:", e)
                continue

            results = self.face_detector.process(rgb_frame)
            if not results or not results.detections:
                continue

            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                frame_h, frame_w, _ = frame.shape

                x = max(0, int(bboxC.xmin * frame_w))
                y = max(0, int(bboxC.ymin * frame_h))
                w = max(1, int(bboxC.width * frame_w))
                h = max(1, int(bboxC.height * frame_h))

                try:
                    face = cv2.cvtColor(rgb_frame[y:y+h, x:x+w], cv2.COLOR_RGB2GRAY)
                    face = cv2.resize(face, (200, 200))
                except Exception as e:
                    print("❌ Error processing face:", e)
                    continue

                if self.recognizer_trained:
                    try:
                        label, confidence = self.recognizer.predict(face)
                        print(f"🔍 Recognized as label {label}, confidence: {confidence}")
                    except Exception as e:
                        print("❌ Error during prediction:", e)
                        continue

                    if confidence < self.confidence_threshold:
                        full_name = self.label_map.get(label, "Unknown")
                        print(f"✅ Matched Face: {full_name}")
                        app = MDApp.get_running_app()
                        Clock.schedule_once(lambda dt: app.authenticate_user_by_face(full_name))
                        self.is_scanning = False
                        return
                    else:
                        print("⚠️ Face detected but confidence too high.")
        threading.Thread(target=speak, args=("Face not recognized. Please try again.",), daemon=True).start()

    def _initialize_recognizer(self):
        """Initialize OpenCV Face Recognizer safely."""
        try:
            self.recognizer = cv2.face.EigenFaceRecognizer_create()
            print("✅ EigenFaceRecognizer created.")
        except AttributeError as e:
            print("⚠️ EigenFaceRecognizer_create failed:", e)
            try:
                self.recognizer = cv2.face.FisherFaceRecognizer_create()
                print("✅ FisherFaceRecognizer created.")
            except AttributeError as e2:
                print("❌ Error: OpenCV Face Recognizer not found! Ensure opencv-contrib-python is installed.", e2)
                self.recognizer = None  # Prevent crashes if no recognizer is available
