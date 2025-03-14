from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

add_announcement_kv = """
<AddAnnouncementScreen>:
    name: "add_announcement"
    MDFloatLayout:
        Image:
            id: bg_image
            source: ""
            allow_stretch: True
            keep_ratio: False
            size_hint: 1, 1

        # Large logo image
        Image:
            source: "images/newto.png"
            size_hint: None, None
            size: dp(150), dp(150)
            pos_hint: {"center_x": 0.5, "top": 0.90}

        MDLabel:
            text: "Add Announcement"
            font_style: "H5"
            halign: "center"
            pos_hint: {"center_x": 0.5, "center_y": 0.70}

        MDTextField:
            id: announcement_title
            hint_text: "Title"
            pos_hint: {"center_x": 0.5, "center_y": 0.60}
            size_hint_x: 0.8

        MDTextField:
            id: announcement_content
            hint_text: "Content"
            pos_hint: {"center_x": 0.5, "center_y": 0.50}
            size_hint_x: 0.8
            multiline: True

        MDRaisedButton:
            text: "Submit"
            size_hint_y: None
            height: dp(45)
            pos_hint: {"center_x": 0.5, "center_y": 0.40}
            on_release:
                app.submit_announcement()

        MDIconButton:
            icon: "arrow-left"
            user_font_size: "24sp"
            pos_hint: {"x": 0.02, "top": 0.98}
            on_release:
                app.root.current = "admin_dashboard"
"""

Builder.load_string(add_announcement_kv)

class AddAnnouncementScreen(MDScreen):
    pass
