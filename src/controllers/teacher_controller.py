from __future__ import annotations

from typing import Any

from tkinter import messagebox

from src.models.teacher_model import TeacherModel
from src.services.teacher_service import TeacherService
from src.views.teacher_view import TeacherView


class TeacherController:
    def __init__(self, app: Any, router: Any) -> None:
        self.app = app
        self.router = router
        self.service = TeacherService()
        self.view: TeacherView | None = None

    def build_view(self) -> TeacherView:
        self.view = TeacherView(
            self.app.root,
            on_save=self.on_save,
            on_update=self.on_update,
            on_delete=self.on_delete,
            on_refresh=self.on_refresh,
            on_search=self.on_search,
            on_back=self.on_back,
            assets_dir=self.app.assets_dir,
        )
        return self.view

    def on_show(self, **_: object) -> None:
        self._reload_table()

    def on_back(self) -> None:
        self.router.show("dashboard")

    def _reload_table(self) -> None:
        teachers = self.service.get_all_teachers()
        if self.view is not None:
            self.view.set_table_rows(teachers)

    @staticmethod
    def _validate_email(email: str) -> bool:
        return ("@" in email) and ("." in email)

    def on_save(self, name: str, phone: str, email: str, security_q: str, security_a: str, password: str):
        if not name or not phone or not email or not password:
            return False, "Vui lòng nhập đủ Tên, SĐT, Email và Mật khẩu!"
        if not self._validate_email(email):
            return False, "Email không hợp lệ!"

        teacher = TeacherModel(
            teacher_id=None,
            name=name,
            phone=phone,
            email=email,
            security_q=security_q or "default",
            security_a=security_a or "default",
            password=password,
        )
        ok, msg = self.service.create_teacher(teacher)
        if ok:
            self._reload_table()
        return ok, msg

    def on_update(
        self,
        teacher_id: str,
        name: str,
        phone: str,
        email: str,
        security_q: str,
        security_a: str,
        password: str,
    ):
        if not teacher_id:
            return False, "Chưa chọn giảng viên để cập nhật!"
        try:
            t_id = int(teacher_id)
        except ValueError:
            return False, "Teacher_id phải là số nguyên!"

        if not name or not phone or not email or not password:
            return False, "Vui lòng nhập đủ Tên, SĐT, Email và Mật khẩu!"
        if not self._validate_email(email):
            return False, "Email không hợp lệ!"

        teacher = TeacherModel(
            teacher_id=t_id,
            name=name,
            phone=phone,
            email=email,
            security_q=security_q or "default",
            security_a=security_a or "default",
            password=password,
        )
        ok, msg = self.service.update_teacher(teacher)
        if ok:
            self._reload_table()
        return ok, msg

    def on_delete(self, teacher_id: str):
        if not teacher_id:
            return False, "Chưa chọn giảng viên để xóa!"
        try:
            t_id = int(teacher_id)
        except ValueError:
            return False, "Teacher_id phải là số nguyên!"

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa giảng viên này?") is False:
            return False, "Đã hủy."

        ok, msg = self.service.delete_teacher(t_id)
        if ok:
            self._reload_table()
        return ok, msg

    def on_refresh(self):
        self._reload_table()
        return True, "Đã làm mới danh sách."

    def on_search(self, keyword: str):
        teachers = self.service.search_teachers(keyword)
        if self.view is not None:
            self.view.set_table_rows(teachers)
        return True, f"Tìm thấy {len(teachers)} kết quả."

