from __future__ import annotations

from typing import Any

from src.views.login_view import LoginView
from services.teacher_service import TeacherService


class LoginController:
    def __init__(self, app: Any, router: Any) -> None:
        self.app = app
        self.router = router
        self.teacher_service = TeacherService()

    def build_view(self) -> LoginView:
        return LoginView(self.app.root, on_login=self.handle_login, assets_dir=self.app.assets_dir)

    def on_show(self, **_: object) -> None:
        return

    def handle_login(self, username_or_email: str, password: str) -> None:
        # if not username_or_email or not password:
        #     LoginView.show_warning("Please enter both Email/Username and Password.")
        #     return
        #
        # try:
        #     is_valid = self.teacher_service.authenticate(username_or_email, password)
        # except Exception as exc:  # noqa: BLE001
        #     LoginView.show_error(f"Database error: {exc}")
        #     return
        #
        # if not is_valid:
        #     LoginView.show_error("Invalid credentials.")
        #     return

        self.router.show("dashboard")

