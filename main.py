import os
import shutil
import datetime
import time
import threading

import firebase_admin
from firebase_admin import credentials, firestore

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.metrics import dp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from plyer import filechooser

# TTS dependencies
import pygame  # for audio playback
from gtts import gTTS  # for generating speech from text

# Screens
from screens.user_login_screen import UserLoginScreen
from screens.admin_dashboard_screen import AdminDashboardScreen
from screens.add_user_screen import AddUserScreen
from screens.add_announcement_screen import AddAnnouncementScreen
from screens.add_report_screen import AddReportScreen
from screens.facerecog import FaceRecogScreen
from screens.objectrecog import ObjectRecogScreen
from screens.tts_scan_screen import TTSScanScreen

Window.size = (360, 640)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "visioappdataServiceAccountKey.json")

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    raise FileNotFoundError(
        f"Could not find '{SERVICE_ACCOUNT_PATH}'. Ensure the JSON key is placed correctly."
    )

cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()


class ScreenManagement(ScreenManager):
    pass


class StartupScreen(Screen):
    pass


class UserHomeScreen(Screen):
    pass


class NextScreen(Screen):
    page_text = StringProperty("Adjust Font Size")
    font_size = NumericProperty(24)


class DashboardScreen(Screen):
    pass


class ProfileScreen(Screen):
    pass


class FontSizeScreen(Screen):
    pass


class VoiceSpeedScreen(Screen):
    pass


################################################################
# History Screen
################################################################
class HistoryScreen(Screen):
    """
    Displays a table with Date/Time, Feature Used, and User Classification.
    """
    def on_pre_enter(self, *args):
        self.build_history_table()

    def build_history_table(self):
        self.clear_widgets()
        main_layout = MDBoxLayout(orientation="vertical")

        # Top Bar with Back Button + Title
        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
        )
        with top_bar.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(rgba=MDApp.get_running_app().theme_cls.primary_color)
            self.top_rect = Rectangle()

        def update_rect(*_):
            self.top_rect.size = top_bar.size
            self.top_rect.pos = top_bar.pos

        top_bar.bind(size=update_rect, pos=update_rect)

        back_button = MDIconButton(
            icon="arrow-left",
            pos_hint={"center_y": 0.5},
            on_release=lambda x: self.go_back()
        )
        top_bar.add_widget(back_button)

        title_label = MDLabel(
            text="History",
            halign="center",
            valign="center",
            color=(1, 1, 1, 1),
            font_style="H6",
            size_hint_x=0.9
        )
        top_bar.add_widget(title_label)
        main_layout.add_widget(top_bar)

        column_data = [
            ("Date/Time", dp(40)),
            ("Feature Used", dp(40)),
            ("User Class.", dp(40)),
        ]

        docs = db.collection("history").get()
        row_data = []
        for doc in docs:
            data = doc.to_dict()
            date_time = data.get("date_time", "")
            feature = data.get("feature_used", "")
            classification = data.get("user_classification", "")
            row_data.append((date_time, feature, classification))

        data_table = MDDataTable(
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint=(0.9, 0.8),
            use_pagination=True,
            column_data=column_data,
            row_data=row_data
        )
        main_layout.add_widget(data_table)
        self.add_widget(main_layout)

    def go_back(self):
        MDApp.get_running_app().sm.current = "profile"






################################################################
# Object Recognition Screen
################################################################


################################################################
# TTS Screen
################################################################



################################################################
# Main App
################################################################
class MainApp(MDApp):
    selected_facial_image = None
    global_font_size = NumericProperty(16)
    global_voice_speed = NumericProperty(1.0)

    def build(self):
        self.theme_cls.theme_style = "Light"

        style_kv = r"""
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp
#:import FitImage kivymd.uix.fitimage.FitImage

<MDRaisedButton>:
    elevation: 2
    font_size: f"{app.global_font_size}sp"
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1)
        Line:
            width: dp(2)
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(2))

<MDRectangleFlatIconButton>:
    size_hint_x: 1
    height: dp(50)
    font_size: f"{app.global_font_size}sp"
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1)
        Line:
            width: dp(2)
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(2))

<MDLabel>:
    color: (1,1,1,1) if app.theme_cls.theme_style == "Dark" else (0,0,0,1)
    font_size: f"{app.global_font_size}sp"

<MDTextField>:
    font_size: f"{app.global_font_size}sp"
    text_color_normal: (1,1,1,1) if app.theme_cls.theme_style == "Dark" else (0,0,0,1)
    text_color_focus: (1,1,1,1) if app.theme_cls.theme_style == "Dark" else (0,0,0,1)
    hint_text_color_normal: (0.7,0.7,0.7,1) if app.theme_cls.theme_style == "Dark" else (0,0,0,1)
    hint_text_color_focus: (0.7,0.7,0.7,1) if app.theme_cls.theme_style == "Dark" else (0,0,0,1)
    line_color_normal: (1,1,1,1) if app.theme_cls.theme_style == "Dark" else (0,0,0,1)
    line_color_focus: (0.7,0.7,0.7,1) if app.theme_cls.theme_style == "Dark" else (0,0,0,1)

<NextScreen>:
    name: "font_adjust"
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(20)
        padding: dp(20)
        MDLabel:
            id: page_label
            text: root.page_text
            halign: "center"
            font_size: root.font_size
        MDSlider:
            id: font_slider
            min: 12
            max: 48
            value: root.font_size
            on_value: root.font_size = self.value
        MDRaisedButton:
            text: "Go to Dashboard"
            pos_hint: {"center_x": 0.5}
            on_release: app.go_dashboard()

<DashboardScreen>:
    name: "dashboard"
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(56)
            canvas.before:
                Color:
                    rgba: app.theme_cls.primary_color
                Rectangle:
                    pos: self.pos
                    size: self.size
            MDLabel:
                text: "Dashboard"
                halign: "center"
                font_style: "H5"
                size_hint_x: 0.8
                color: (1, 1, 1, 1)
            MDIconButton:
                icon: "theme-light-dark"
                on_release: app.toggle_theme()
                size_hint_x: 0.2
                text_color: (1, 1, 1, 1)

        MDBottomNavigation:
            elevation: 8
            panel_color: app.theme_cls.primary_dark
            text_color_active: 1, 1, 1, 1
            text_color_normal: 1, 1, 1, 0.6
            selected_color_background: 0, 0, 0, 0
            radius: [20, 20, 0, 0]

            MDBottomNavigationItem:
                name: 'face'
                text: 'Face'
                icon: 'face-recognition'
                on_tab_press: app.go_face_recog_screen()
                MDLabel:
                    text: "Face Recognition"
                    halign: "center"

            MDBottomNavigationItem:
                name: 'object'
                text: 'Object'
                icon: 'cube'
                on_tab_press: app.go_object_recog_screen()
                MDLabel:
                    text: "Object Recognition Screen"
                    halign: "center"

            MDBottomNavigationItem:
                name: 'tts'
                text: 'TTS'
                icon: 'volume-high'
                on_tab_press: app.go_tts_screen()
                MDLabel:
                    text: "Text-to-Speech Screen"
                    halign: "center"

            MDBottomNavigationItem:
                name: 'profile'
                text: 'Profile'
                icon: 'account'
                on_tab_press: app.go_profile()
                MDLabel:
                    text: "User Profile Screen"
                    halign: "center"

<ProfileScreen>:
    name: "profile"
    MDFloatLayout:
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"x": 0, "top": 1}
            on_release: app.go_dashboard()
        FitImage:
            source: "images/newto.png"
            size_hint: None, None
            width: dp(200)
            height: dp(100)
            pos_hint: {"center_x": 0.5, "top": 0.95}
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(20)
            padding: dp(20)
            size_hint: 0.8, None
            height: self.minimum_height
            pos_hint: {"center_x": 0.5, "top": 0.7}
            MDRectangleFlatIconButton:
                text: "Customize Font Size"
                icon: "format-size"
                on_release: app.go_font_size_screen()
            MDRectangleFlatIconButton:
                text: "Customize Voice Speed"
                icon: "microphone"
                on_release: app.go_customize_voice_speed()
            MDRectangleFlatIconButton:
                text: "History"
                icon: "history"
                on_release: app.go_history()
            MDRectangleFlatIconButton:
                text: "Toggle Theme"
                icon: "theme-light-dark"
                on_release: app.toggle_theme()
            MDRectangleFlatIconButton:
                text: "Logout"
                icon: "logout"
                on_release: app.logout_user()

<StartupScreen>:
    name: "startup"
    BoxLayout:
        orientation: "vertical"
        Carousel:
            id: startup_carousel
            on_index: app.update_dot_indicator(self.index)
            size_hint_y: 0.9
            BoxLayout:
                orientation: "vertical"
                Image:
                    source: "images/1.png"
                    allow_stretch: True
                    keep_ratio: False
            BoxLayout:
                orientation: "vertical"
                MDRelativeLayout:
                    Image:
                        source: "images/2.png"
                        allow_stretch: True
                        keep_ratio: False
                    MDFlatButton:
                        text: "Skip"
                        size_hint: None, None
                        size: dp(80), dp(40)
                        pos_hint: {"right": 0.95, "top": 0.95}
                        on_release: app.skip_onboarding()
            BoxLayout:
                orientation: "vertical"
                MDRelativeLayout:
                    Image:
                        source: "images/3.png"
                        allow_stretch: True
                        keep_ratio: False
                    MDFlatButton:
                        text: "Skip"
                        size_hint: None, None
                        size: dp(80), dp(40)
                        pos_hint: {"right": 0.95, "top": 0.95}
                        on_release: app.skip_onboarding()
            BoxLayout:
                orientation: "vertical"
                MDRelativeLayout:
                    Image:
                        source: "images/4.png"
                        allow_stretch: True
                        keep_ratio: False
                    MDRaisedButton:
                        text: "Get Started"
                        size_hint: None, None
                        size: dp(150), dp(50)
                        pos_hint: {"center_x": 0.5, "center_y": 0.05}
                        on_release: app.skip_onboarding()
        AnchorLayout:
            size_hint_y: 0.1
            anchor_x: 'center'
            anchor_y: 'center'
            MDBoxLayout:
                orientation: "horizontal"
                spacing: dp(2)
                adaptive_size: True
                MDIcon:
                    id: dot1
                    icon: "checkbox-blank-circle"
                    size_hint: None, None
                    size: dp(6), dp(6)
                    color: (1, 0.5, 0, 1)
                MDIcon:
                    id: dot2
                    icon: "checkbox-blank-circle"
                    size_hint: None, None
                    size: dp(6), dp(6)
                    color: (0.7, 0.7, 0.7, 1)
                MDIcon:
                    id: dot3
                    icon: "checkbox-blank-circle"
                    size_hint: None, None
                    size: dp(6), dp(6)
                    color: (0.7, 0.7, 0.7, 1)
                MDIcon:
                    id: dot4
                    icon: "checkbox-blank-circle"
                    size_hint: None, None
                    size: dp(6), dp(6)
                    color: (0.7, 0.7, 0.7, 1)

<FontSizeScreen>:
    name: "font_size_screen"
    MDFloatLayout:
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"x": 0, "top": 1}
            on_release: app.go_profile()
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(20)
            padding: dp(20)
            size_hint: 1, 1
            MDLabel:
                id: sample_label
                text: "The quick brown fox jumps over the lazy dog"
                halign: "center"
            AnchorLayout:
                anchor_x: "center"
                anchor_y: "center"
                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: dp(10)
                    size_hint: None, None
                    size: self.minimum_size
                    MDRaisedButton:
                        text: "Small"
                        on_release: app.set_preview_font_size("small")
                    MDRaisedButton:
                        text: "Medium"
                        on_release: app.set_preview_font_size("medium")
                    MDRaisedButton:
                        text: "Large"
                        on_release: app.set_preview_font_size("large")
            MDRaisedButton:
                text: "Submit"
                size_hint_y: None
                height: dp(48)
                pos_hint: {"center_x": 0.5}
                on_release: app.apply_font_size()

<VoiceSpeedScreen>:
    name: "voice_speed"
    MDFloatLayout:
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"x": 0, "top": 1}
            on_release: app.go_profile()
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(20)
            padding: dp(20)
            size_hint: 1, 1
            MDLabel:
                text: "Adjust Voice Speed"
                halign: "center"
                font_style: "H5"
            MDSlider:
                id: speed_slider
                min: 0.5
                max: 2.0
                value: app.global_voice_speed
                step: 0.1
                hint: False
                on_value: app.set_voice_speed(self.value)
            MDRaisedButton:
                text: "Test Voice"
                pos_hint: {"center_x": 0.5}
                on_release: app.test_voice_speed()
            MDRaisedButton:
                text: "Apply Speed"
                pos_hint: {"center_x": 0.5}
                on_release: app.apply_voice_speed()
"""
        Builder.load_string(style_kv)

        self.sm = ScreenManagement()

        # Add screens
        self.sm.add_widget(StartupScreen(name="startup"))
        self.sm.add_widget(UserLoginScreen(name="user_login"))
        self.sm.add_widget(AdminDashboardScreen(name="admin_dashboard"))
        self.sm.add_widget(AddUserScreen(name="add_user"))
        self.sm.add_widget(AddAnnouncementScreen(name="add_announcement"))
        self.sm.add_widget(AddReportScreen(name="add_report"))
        self.sm.add_widget(UserHomeScreen(name="user_home"))
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(ProfileScreen(name="profile"))
        self.sm.add_widget(FontSizeScreen(name="font_size_screen"))
        self.sm.add_widget(VoiceSpeedScreen(name="voice_speed"))
        self.sm.add_widget(HistoryScreen(name="history"))

        # Face & Object
        self.sm.add_widget(FaceRecogScreen(name="face_recognition"))
        self.sm.add_widget(ObjectRecogScreen(name="object_recognition"))

        # TTS
        self.sm.add_widget(TTSScanScreen(name="tts_scan"))

        self.sm.current = "startup"
        self.update_background()
        return self.sm


    def go_add_user(self):
        """Navigate to the Add User screen."""

        self.sm.current = "add_user"

    def on_start(self):
        """Set up role & grade dropdown menus in AddUserScreen."""
        add_user_screen = self.sm.get_screen("add_user")
        role_menu_items = [
            {"text": "Student", "viewclass": "OneLineListItem", "on_release": lambda x="Student": self.set_role(x)},
            {"text": "Teacher", "viewclass": "OneLineListItem", "on_release": lambda x="Teacher": self.set_role(x)},
        ]
        self.role_menu = MDDropdownMenu(
            caller=add_user_screen.ids.user_role,
            items=role_menu_items,
            width_mult=3,
        )

        grade_menu_items = [
            {"text": str(i), "viewclass": "OneLineListItem", "on_release": lambda x=str(i): self.set_grade(x)}
            for i in range(1, 7)
        ]
        self.grade_menu = MDDropdownMenu(
            caller=add_user_screen.ids.user_grade,
            items=grade_menu_items,
            width_mult=3,
        )

    # THEME & BACKGROUND
    def toggle_theme(self):
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )
        self.update_background()

    def update_background(self):
        for screen in self.sm.screens:
            if screen.name != "user_login" and "bg_image" in screen.ids:
                bg_source = (
                    "images/black.jpg"
                    if self.theme_cls.theme_style == "Dark"
                    else "images/dirty.jpg"
                )
                screen.ids["bg_image"].source = bg_source

    # ONBOARDING
    def skip_onboarding(self):
        self.sm.current = "user_login"

    def update_dot_indicator(self, index):
        startup_screen = self.sm.get_screen("startup")
        dot1 = startup_screen.ids.dot1
        dot2 = startup_screen.ids.dot2
        dot3 = startup_screen.ids.dot3
        dot4 = startup_screen.ids.dot4
        default_color = (0.7, 0.7, 0.7, 1)
        highlight_color = (0, 0, 1, 0.5)
        dot1.color = dot2.color = dot3.color = dot4.color = default_color
        if index == 0:
            dot1.color = highlight_color
        elif index == 1:
            dot2.color = highlight_color
        elif index == 2:
            dot3.color = highlight_color
        elif index == 3:
            dot4.color = highlight_color

    # ROLE & GRADE
    def set_role(self, role):
        screen = self.sm.get_screen("add_user")
        screen.ids.user_role.text = role
        self.role_menu.dismiss()

    def set_grade(self, grade):
        screen = self.sm.get_screen("add_user")
        screen.ids.user_grade.text = grade
        self.grade_menu.dismiss()

    # USER LOGIN
    def sign_in_user(self):
        screen = self.sm.get_screen("user_login")
        username = screen.ids.user_username.text.strip()
        password = screen.ids.user_password.text.strip()

        if not username or not password:
            self.show_dialog("Error", "Please enter both username and password.")
            return

        # Admin check
        if username == "admin" and password == "admin123":
            self.show_dialog("Success", "Admin login successful!")
            self.sm.current = "admin_dashboard"
            return

        user_doc = db.collection("users").document(username).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            if user_data.get("password") == password:
                full_name = user_data.get("full_name", username)
                dialog = MDDialog(
                    title="Welcome",
                    text=f"Welcome, {full_name}",
                    size_hint=(0.8, 0.3),
                    buttons=[
                        MDRaisedButton(
                            text="OK",
                            on_release=lambda x: self.dismiss_welcome_dialog(dialog, full_name)
                        )
                    ],
                )
                dialog.open()
            else:
                self.show_dialog("Error", "Invalid password.")
        else:
            self.show_dialog("Error", "User does not exist.")

    def dismiss_welcome_dialog(self, dialog, full_name):
        dialog.dismiss()
        self.sm.current = "dashboard"

    def authenticate_user_by_face(self, full_name):
        users_ref = db.collection("users")
        query = users_ref.where("full_name", "==", full_name).limit(1).stream()
        user_data = None
        for doc in query:
            user_data = doc.to_dict()
            break

        if user_data:
            username = user_data.get("username", full_name)
            print(f"✅ User found: {username} ({full_name})")
            dialog = MDDialog(
                title="Welcome",
                text=f"Welcome, {full_name}!",
                size_hint=(0.8, 0.3),
                buttons=[
                    MDRaisedButton(
                        text="OK",
                        on_release=lambda x: self.dismiss_welcome_dialog(dialog, full_name)
                    )
                ],
            )
            dialog.open()
        else:
            print("❌ User not found in database.")
            self.show_dialog("Error", "Face not recognized. Please log in manually.")

    # DASHBOARD NAV
    def go_face_recog_screen(self):
        self.sm.current = "face_recognition"

    def go_object_recog_screen(self):
        self.sm.current = "object_recognition"

    def go_tts_screen(self):
        self.sm.current = "tts_scan"

    def text_to_speech(self):
        # If used in older code, just route to the same place
        self.go_tts_screen()

    def go_profile(self):
        self.sm.current = "profile"

    def go_dashboard(self):
        self.sm.current = "dashboard"

    # LOGOUT
    def logout_user(self):
        dialog = MDDialog(
            title="Logout Confirmation",
            text="Are you sure you want to logout?",
            size_hint=(0.8, 0.3),
            buttons=[
                MDRaisedButton(text="YES", on_release=lambda x: self.confirm_logout(dialog)),
                MDFlatButton(text="NO", on_release=lambda x: dialog.dismiss()),
            ],
        )
        dialog.open()

    def logout_admin(self):
        dialog = MDDialog(
            title="Logout Confirmation",
            text="Are you sure you want to logout?",
            size_hint=(0.8, 0.3),
            buttons=[
                MDRaisedButton(text="YES", on_release=lambda x: self.confirm_logout(dialog)),
                MDFlatButton(text="NO", on_release=lambda x: dialog.dismiss()),
            ],
        )
        dialog.open()

    def confirm_logout(self, dialog):
        dialog.dismiss()
        self.sm.current = "user_login"

    # ADD USER
    def submit_user(self):
        screen = self.sm.get_screen("add_user")
        role = screen.ids.user_role.text.strip()
        name = screen.ids.user_name.text.strip()
        age = screen.ids.user_age.text.strip()
        username = screen.ids.user_username.text.strip()
        password = screen.ids.user_password.text.strip()
        grade = screen.ids.user_grade.text.strip()

        if not role or role == "Select Role":
            self.show_dialog("Error", "Please select a role (Student or Teacher).")
            return
        if not name or not age or not username or not password:
            self.show_dialog("Error", "Please fill out all fields.")
            return
        if role == "Student" and (not grade or grade == "Select Grade"):
            self.show_dialog("Error", "Please select a grade for the student.")
            return

        user_data = {
            "role": role,
            "full_name": name,
            "age": age,
            "password": password,
            "grade": grade if role == "Student" else "",
        }
        db.collection("users").document(username).set(user_data)

        if self.selected_facial_image:
            destination_folder = os.path.join("images", "userfacialimage")
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            ext = os.path.splitext(self.selected_facial_image)[1]
            new_filename = username + ext
            dest_path = os.path.join(destination_folder, new_filename)
            shutil.copy(self.selected_facial_image, dest_path)
            self.selected_facial_image = None

        self.show_dialog("Success", f"{role} '{name}' added successfully!")
        screen.ids.user_role.text = "Select Role"
        screen.ids.user_name.text = ""
        screen.ids.user_age.text = ""
        screen.ids.user_username.text = ""
        screen.ids.user_password.text = ""
        screen.ids.user_grade.text = "Select Grade"
        self.sm.current = "admin_dashboard"

    def upload_facial_image(self):
        file_paths = filechooser.open_file(title="Choose Facial Image")
        if file_paths:
            self.selected_facial_image = file_paths[0]
            self.show_dialog("Success", f"Selected image: {os.path.basename(self.selected_facial_image)}")
        else:
            self.show_dialog("Error", "No file selected.")

    # ANNOUNCEMENT
    def submit_announcement(self):
        screen = self.sm.get_screen("add_announcement")
        title = screen.ids.announcement_title.text.strip()
        content = screen.ids.announcement_content.text.strip()
        if not title or not content:
            self.show_dialog("Error", "Please fill out all fields.")
            return
        db.collection("announcements").add({"title": title, "content": content})
        self.show_dialog("Success", f"Announcement '{title}' created!")
        screen.ids.announcement_title.text = ""
        screen.ids.announcement_content.text = ""
        self.sm.current = "admin_dashboard"

    # REPORT
    def submit_report(self):
        screen = self.sm.get_screen("add_report")
        title = screen.ids.report_title.text.strip()
        description = screen.ids.report_description.text.strip()
        if not title or not description:
            self.show_dialog("Error", "Please fill out all fields.")
            return
        db.collection("reports").add({"title": title, "description": description})
        self.show_dialog("Success", f"Report '{title}' created!")
        screen.ids.report_title.text = ""
        screen.ids.report_description.text = ""
        self.sm.current = "admin_dashboard"

    # DIALOG UTILITY
    def show_dialog(self, title, text):
        dialog = MDDialog(title=title, text=text, size_hint=(0.8, 0.3))
        dialog.open()

    # FONT SIZE
    def go_font_size_screen(self):
        self.sm.current = "font_size_screen"

    def set_preview_font_size(self, size_choice):
        if size_choice == "small":
            self.global_font_size = 16
        elif size_choice == "medium":
            self.global_font_size = 24
        elif size_choice == "large":
            self.global_font_size = 32

        if self.sm.current == "font_size_screen":
            fs_screen = self.sm.get_screen("font_size_screen")
            fs_screen.ids.sample_label.font_size = f"{self.global_font_size}sp"

    def apply_font_size(self):
        self.sm.current = "dashboard"
        self.show_dialog("Font Size", "Font size updated successfully!")

    # VOICE SPEED
    def go_customize_voice_speed(self):
        self.sm.current = "voice_speed"

    def set_voice_speed(self, value):
        self.global_voice_speed = value

    def test_voice_speed(self):
        phrase = "The Quick Brown Fox Jumps Over The Lazy Dog"
        self.show_dialog("Test Voice", f"Playing TTS at speed {self.global_voice_speed:.1f}:\n\n{phrase}")

    def apply_voice_speed(self):
        self.show_dialog("Voice Speed", f"Voice speed set to {self.global_voice_speed:.1f}x!")
        self.sm.current = "profile"

    # HISTORY
    def go_history(self):
        self.sm.current = "history"

    def store_history(self, feature_used, user_classification="Regular User"):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        doc_data = {
            "date_time": now,
            "feature_used": feature_used,
            "user_classification": user_classification,
        }
        db.collection("history").add(doc_data)


if __name__ == "__main__":
    MainApp().run()
