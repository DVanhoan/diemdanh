from __future__ import annotations

from typing import Any

from tkinter import messagebox

from models.student_model import StudentModel
from src.views.student_view import StudentView
from services.student_service import StudentService


class StudentController:
    def __init__(self, app: Any, router: Any) -> None:
        self.app = app
        self.router = router
        self.service = StudentService()
        self.view: StudentView | None = None

    def build_view(self) -> StudentView:
        self.view = StudentView(
            self.app.root,
            on_save=self.on_save,
            on_update=self.on_update,
            on_delete=self.on_delete,
            on_refresh=self.on_refresh,
            on_search=self.on_search,
            on_capture=self.on_capture,
            on_back=self.on_back,
            assets_dir=self.app.assets_dir,
        )
        return self.view

    def on_show(self, **_: object) -> None:
        self._reload_table()

    def on_back(self) -> None:
        self.router.show("dashboard")

    def _reload_table(self) -> None:
        students = self.service.get_all_students()
        if self.view is not None:
            self.view.set_table_rows(students)

    def on_save(
        self,
        st_id,
        name,
        class_name,
        phone,
        email,
        year,
        semester,
        gender,
        dob,
        address,
        photo_sample,
        dep=None,
        course=None,
        roll=None,
    ) -> None:
        # 1. Validate dữ liệu đầu vào
        if not st_id or not name or not class_name:
            return False, "Vui lòng nhập đủ Mã SV, Tên và Lớp!"

        try:
            st_id_int = int(st_id)
        except ValueError:
            return False, "Mã sinh viên phải là số nguyên!"

        # 2. Tạo đối tượng Model
        new_student = StudentModel(
            student_id=st_id_int,
            name=name,
            class_name=class_name,
            phone=phone,
            email=email,
            dep=dep,
            course=course,
            year=year,
            semester=semester,
            roll=roll,
            gender=gender,
            dob=dob,
            address=address,
            photo_sample=photo_sample,
        )

        # 3. Gọi Service để thực hiện lưu xuống DB
        ok, msg = self.service.create_student(new_student)
        if ok:
            self._reload_table()
        return ok, msg


    def on_update(
        self,
        st_id,
        name,
        class_name,
        phone,
        email,
        year,
        semester,
        gender,
        dob,
        address,
        photo_sample,
        dep=None,
        course=None,
        roll=None,
    ) -> None:
        # 1. Validate dữ liệu đầu vào
        if not st_id or not name or not class_name:
            return False, "Vui lòng nhập đủ Mã SV, Tên và Lớp!"

        try:
            st_id_int = int(st_id)
        except ValueError:
            return False, "Mã sinh viên phải là số nguyên!"

        # 2. Tạo đối tượng Model
        updated_student = StudentModel(
            student_id=st_id_int,
            name=name,
            class_name=class_name,
            phone=phone,
            email=email,
            dep=dep,
            course=course,
            year=year,
            semester=semester,
            roll=roll,
            gender=gender,
            dob=dob,
            address=address,
            photo_sample=photo_sample,
        )

        # 3. Gọi Service để thực hiện cập nhật xuống DB
        ok, msg = self.service.update_student(updated_student)
        if ok:
            self._reload_table()
        return ok, msg

    def on_delete(self, st_id) -> None:
        if not st_id:
            return False, "Chưa chọn sinh viên để xóa!"
        ok, msg = self.service.delete_student(st_id)
        if ok:
            self._reload_table()
        return ok, msg

    def on_refresh(self) -> None:
        self._reload_table()
        return True, "Đã làm mới danh sách."

    def on_search(self, search_type: str, keyword: str):
        students = self.service.search_students(search_type, keyword)
        if self.view is not None:
            self.view.set_table_rows(students)
        return True, f"Tìm thấy {len(students)} kết quả."

    @staticmethod
    def on_capture() -> None:
        messagebox.showinfo("Chụp ảnh mẫu", "Chức năng chụp ảnh sẽ được nối ở module camera.")

