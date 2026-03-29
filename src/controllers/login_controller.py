from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from src.database import Database
from src.models.student_model import StudentModel
from src.models.teacher_model import TeacherModel
from src.views.dashboard_view import DashboardView
from src.views.login_view import LoginView
from src.views.student_view import StudentView


class LoginController:

    STANDARD_WIDTH = 1180
    STANDARD_HEIGHT = 680
    STANDARD_MIN_WIDTH = 1100
    STANDARD_MIN_HEIGHT = 640

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Face Recognition Attendance System")
        self._apply_standard_window_geometry(center=True)

        self.project_root = Path(__file__).resolve().parents[2]
        self.assets_dir = self.project_root / "assets"

        self.database = Database()
        self.teacher_model = TeacherModel(self.database)
        self.student_model = StudentModel(self.database)

        self.current_view = None

        self._apply_window_icon()
        self._prepare_database()

        #auto login with admin: admin@gmail.com , pass:123
        self.handle_login("admin@gmail.com", "123")

        # self.show_login_view()

    def _apply_standard_window_geometry(self, *, center: bool) -> None:
        self.root.minsize(self.STANDARD_MIN_WIDTH, self.STANDARD_MIN_HEIGHT)
        if not center:
            self.root.geometry(f"{self.STANDARD_WIDTH}x{self.STANDARD_HEIGHT}")
            return

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = max(0, int((screen_w - self.STANDARD_WIDTH) / 2))
        y = max(0, int((screen_h - self.STANDARD_HEIGHT) / 2))
        self.root.geometry(f"{self.STANDARD_WIDTH}x{self.STANDARD_HEIGHT}+{x}+{y}")

    def _prepare_database(self) -> None:
        try:
            self.database.initialize_schema()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Database Error", str(exc))

    def _find_icon_file(self) -> Path | None:
        supported = ["*.ico", "*.png", "*.gif"]
        for pattern in supported:
            matches = list(self.assets_dir.glob(pattern))
            if matches:
                return matches[0]
        return None

    def _apply_window_icon(self) -> None:
        icon_path = self._find_icon_file()
        if not icon_path:
            return

        try:
            if icon_path.suffix.lower() == ".ico":
                self.root.iconbitmap(default=str(icon_path))
            else:
                icon_image = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, icon_image)
                self.root._icon_ref = icon_image
        except tk.TclError:
            pass

    def _set_view(self, view: tk.Widget) -> None:
        if self.current_view is not None:
            self.current_view.pack_forget()
            self.current_view.destroy()
        self.current_view = view
        self.current_view.pack(fill="both", expand=True)
        self._apply_standard_window_geometry(center=True)

    def show_login_view(self) -> None:
        login_view = LoginView(self.root, self.handle_login, self.assets_dir)
        self._set_view(login_view)

    def handle_login(self, username_or_email: str, password: str) -> None:
        if not username_or_email or not password:
            LoginView.show_warning("Please enter both Email/Username and Password.")
            return

        try:
            is_valid = self.teacher_model.authenticate(username_or_email, password)
        except Exception as exc:  # noqa: BLE001
            LoginView.show_error(f"Database error: {exc}")
            return

        if not is_valid:
            LoginView.show_error("Invalid credentials.")
            return

        # LoginView.show_info("Login successful.")
        self.show_dashboard_view()

    def show_dashboard_view(self) -> None:
        dashboard_view = DashboardView(
            self.root,
            on_manage_students=self.on_manage_students,
            on_face_recognition=self.on_face_recognition,
            on_attendance_report=self.on_attendance_report,
            on_subjects=self.on_subjects,
            on_statistics=self.on_statistics,
            on_teachers=self.on_teachers,
            on_lessons=self.on_lessons,
            on_view_images=self.on_view_images,
            on_exit=self.on_exit,
            assets_dir=self.assets_dir,
        )
        self._set_view(dashboard_view)

    def on_manage_students(self) -> None:
        student_view = StudentView(
            self.root,
            on_save=self._show_placeholder_save,
            on_update=self._show_placeholder_update,
            on_delete=self._show_placeholder_delete,
            on_refresh=self._show_placeholder_refresh,
            on_capture=self._show_placeholder_capture,
            on_back=self.show_dashboard_view,
            assets_dir=self.assets_dir,
        )
        self._set_view(student_view)

    @staticmethod
    def on_face_recognition() -> None:
        messagebox.showinfo("Face Recognition", "Face Recognition module is next.")

    @staticmethod
    def on_attendance_report() -> None:
        messagebox.showinfo("Attendance Report", "Attendance Report module is next.")

    @staticmethod
    def on_subjects() -> None:
        messagebox.showinfo("Môn học", "Chức năng quản lý môn học sẽ được nối ở bước tiếp theo.")

    @staticmethod
    def on_statistics() -> None:
        messagebox.showinfo("Thống kê", "Chức năng thống kê sẽ được nối ở bước tiếp theo.")

    @staticmethod
    def on_teachers() -> None:
        messagebox.showinfo("Giáo viên", "Chức năng quản lý giáo viên sẽ được nối ở bước tiếp theo.")

    @staticmethod
    def on_lessons() -> None:
        messagebox.showinfo("Buổi học", "Chức năng quản lý buổi học sẽ được nối ở bước tiếp theo.")

    @staticmethod
    def on_view_images() -> None:
        messagebox.showinfo("Xem ảnh", "Chức năng xem ảnh mẫu sẽ được nối ở bước tiếp theo.")

    @staticmethod
    def _show_placeholder_save() -> None:
        messagebox.showinfo("Lưu", "Chức năng Lưu sẽ được nối logic ở bước tiếp theo.")

    @staticmethod
    def _show_placeholder_update() -> None:
        messagebox.showinfo("Cập nhật", "Chức năng Cập nhật sẽ được nối logic ở bước tiếp theo.")

    @staticmethod
    def _show_placeholder_delete() -> None:
        messagebox.showinfo("Xóa", "Chức năng Xóa sẽ được nối logic ở bước tiếp theo.")

    @staticmethod
    def _show_placeholder_refresh() -> None:
        messagebox.showinfo("Làm mới", "Chức năng Làm mới sẽ được nối logic ở bước tiếp theo.")

    @staticmethod
    def _show_placeholder_capture() -> None:
        messagebox.showinfo("Chụp ảnh mẫu", "Chức năng chụp ảnh sẽ được nối ở module camera.")

    def on_exit(self) -> None:
        self.database.close()
        self.root.destroy()

    def run(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.root.mainloop()
