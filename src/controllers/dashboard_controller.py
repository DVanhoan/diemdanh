from __future__ import annotations

from typing import Any

from tkinter import messagebox

from src.views.dashboard_view import DashboardView


class DashboardController:
    def __init__(self, app: Any, router: Any) -> None:
        self.app = app
        self.router = router

    def build_view(self) -> DashboardView:
        return DashboardView(
            self.app.root,
            on_manage_students=self.on_manage_students,
            on_face_recognition=self.on_face_recognition,
            on_attendance_report=self.on_attendance_report,
            on_subjects=self.on_subjects,
            on_statistics=self.on_statistics,
            on_teachers=self.on_teachers,
            on_lessons=self.on_lessons,
            on_view_images=self.on_view_images,
            on_exit=self.on_exit,
            assets_dir=self.app.assets_dir,
        )

    def on_show(self, **_: object) -> None:
        return

    def on_manage_students(self) -> None:
        self.router.show("students")

    def on_face_recognition(self) -> None:
        self.router.show("attendance")

    def on_attendance_report(self) -> None:
       self.router.show("attendance_management")

    @staticmethod
    def on_subjects() -> None:
        messagebox.showinfo("Môn học", "Chức năng quản lý môn học sẽ được nối ở bước tiếp theo.")

    @staticmethod
    def on_statistics() -> None:
        messagebox.showinfo("Thống kê", "Chức năng thống kê sẽ được nối ở bước tiếp theo.")

    def on_teachers(self) -> None:
        self.router.show("teachers")

    @staticmethod
    def on_lessons() -> None:
        messagebox.showinfo("Buổi học", "Chức năng quản lý buổi học sẽ được nối ở bước tiếp theo.")

    @staticmethod
    def on_view_images() -> None:
        messagebox.showinfo("Xem ảnh", "Chức năng xem ảnh mẫu sẽ được nối ở bước tiếp theo.")

    def on_exit(self) -> None:
        self.app.on_exit()

