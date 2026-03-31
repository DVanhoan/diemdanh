from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from src.controllers.attendance_management_controller import AttendanceManagementController
from src.controllers.attendance_controller import AttendanceController
from src.controllers.login_controller import LoginController
from src.controllers.dashboard_controller import DashboardController
from src.controllers.student_controller import StudentController
from src.controllers.teacher_controller import TeacherController


@dataclass(frozen=True)
class Route:
    name: str
    factory: Callable[[], object]


class Router:

    def __init__(self, app: Any) -> None:
        self.app = app

    def show(self, name: str, **payload: Any) -> None:
        if name == "login":
            controller = LoginController(self.app, self)
            view = controller.build_view()
            self.app.set_view(view)
            controller.on_show(**payload)
            return

        if name == "dashboard":
            controller = DashboardController(self.app, self)
            view = controller.build_view()
            self.app.set_view(view)
            controller.on_show(**payload)
            return

        if name == "students":
            controller = StudentController(self.app, self)
            view = controller.build_view()
            self.app.set_view(view)
            controller.on_show(**payload)
            return

        if name == "teachers":
            controller = TeacherController(self.app, self)
            view = controller.build_view()
            self.app.set_view(view)
            controller.on_show(**payload)
            return

        if name == "attendance_management":
            controller = AttendanceManagementController(self.app, self)
            views = controller.build_view()
            self.app.set_view(views)
            controller.on_show(**payload)
            return

        if name == "attendance":
            controller = AttendanceController(self.app, self)
            view = controller.build_view()
            self.app.set_view(view)
            controller.on_show(**payload)
            return


        raise ValueError(f"Unknown route: {name}")

