from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

admin_dashboard_kv = """
<AdminDashboardScreen>:
    name: "admin_dashboard"
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
            size: dp(200), dp(200)
            pos_hint: {"center_x": 0.5, "top": 0.95}

        MDLabel:
            text: "Admin Dashboard"
            font_style: "H5"
            halign: "center"
            pos_hint: {"center_y": 0.65}

        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            size_hint: None, None
            size: dp(250), dp(270)
            pos_hint: {"center_x": 0.5, "center_y": 0.45}

            MDRectangleFlatIconButton:
                icon: "account-plus"
                text: "Add User"
                on_release:
                    app.go_add_user()

            MDRectangleFlatIconButton:
                icon: "bullhorn"
                text: "Announcements"
                on_release:
                    app.go_add_announcement()

            MDRectangleFlatIconButton:
                icon: "file-document"
                text: "Reports"
                on_release:
                    app.go_add_report()

            MDRectangleFlatIconButton:
                icon: "logout"
                text: "Logout"
                on_release:
                    app.logout_admin()
"""

Builder.load_string(admin_dashboard_kv)

class AdminDashboardScreen(MDScreen):
    pass
