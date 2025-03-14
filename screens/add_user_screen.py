from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

add_user_kv = """
<AddUserScreen>:
    name: "add_user"
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
            pos_hint: {"center_x": 0.5, "top": 1}

        MDLabel:
            text: "Add User"
            font_style: "H5"
            halign: "center"
            pos_hint: {"center_x": 0.5, "center_y": 0.80}

        MDDropDownItem:
            id: user_role
            text: "Select Role"
            pos_hint: {"center_x": 0.5, "center_y": 0.70}
            on_release:
                app.role_menu.open()

        MDTextField:
            id: user_name
            hint_text: "Full Name"
            pos_hint: {"center_x": 0.5, "center_y": 0.60}
            size_hint_x: 0.8

        MDTextField:
            id: user_age
            hint_text: "Age"
            pos_hint: {"center_x": 0.5, "center_y": 0.50}
            size_hint_x: 0.8

        MDTextField:
            id: user_username
            hint_text: "Username"
            pos_hint: {"center_x": 0.5, "center_y": 0.40}
            size_hint_x: 0.8

        # Container for the password field and the show/hide icon.
        FloatLayout:
            size_hint: 0.8, None
            height: dp(50)
            pos_hint: {"center_x": 0.5, "center_y": 0.30}

            MDTextField:
                id: user_password
                hint_text: "Password"
                password: True
                size_hint_x: 1
                pos_hint: {"center_x": 0.5, "center_y": 0.5}

            MDIconButton:
                id: show_password_btn
                icon: "eye-off"
                size_hint: None, None
                size: dp(40), dp(40)
                pos_hint: {"center_y": 0.5}
                # Position the icon on the right side of the text field.
                x: user_password.right - self.width - dp(5)
                on_release:
                    user_password.password = not user_password.password
                    self.icon = "eye" if not user_password.password else "eye-off"

        MDDropDownItem:
            id: user_grade
            text: "Select Grade"
            pos_hint: {"center_x": 0.5, "center_y": 0.20}
            on_release:
                app.grade_menu.open()

        MDRaisedButton:
            text: "Upload Facial Image"
            size_hint_y: None
            height: dp(45)
            pos_hint: {"center_x": 0.5, "center_y": 0.12}
            on_release:
                app.upload_facial_image()

        MDRaisedButton:
            text: "Submit"
            size_hint_y: None
            height: dp(45)
            pos_hint: {"center_x": 0.5, "center_y": 0.05}
            on_release:
                app.submit_user()

        MDIconButton:
            icon: "arrow-left"
            user_font_size: "24sp"
            pos_hint: {"x": 0.02, "top": 0.98}
            on_release:
                app.root.current = "admin_dashboard"
"""

Builder.load_string(add_user_kv)

class AddUserScreen(MDScreen):
    pass
