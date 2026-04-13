from __future__ import annotations

from typing import Any

from tkinter import messagebox

from src.models.student_model import StudentModel
# from src.services.face_dataset_service import FaceDatasetService
# from src.services.face_training_service import FaceTrainingService
from src.views.student_view import StudentView
from src.services.student_service import StudentService


class StudentController:
    def __init__(self, app: Any, router: Any) -> None:
        self.app = app
        self.router = router
        self.service = StudentService()
        # self.dataset_service = FaceDatasetService(self.app.assets_dir, self.app.project_root)
        # self.training_service = FaceTrainingService(self.app.project_root)
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
            on_training=self.on_training,
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

    @staticmethod
    def _norm(value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _is_student_changed(self, old: StudentModel, new: StudentModel) -> bool:
        fields = (
            "dep",
            "course",
            "year",
            "semester",
            "name",
            "class_name",
            "roll",
            "gender",
            "dob",
            "email",
            "phone",
            "address",
            "photo_sample",
        )
        return any(self._norm(getattr(old, f, "")) != self._norm(getattr(new, f, "")) for f in fields)

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

        existing_student = self.service.get_student_by_id(st_id_int)
        if existing_student is None:
            return False, "Không tìm thấy sinh viên để cập nhật!"

        if not self._is_student_changed(existing_student, updated_student):
            return True, "Không có dữ liệu thay đổi, danh sách không cần làm mới."

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

    def on_capture(self) -> None:
        if self.view is None:
            return

        student_id_raw = self.view.student_id_var.get().strip()
        if not student_id_raw:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập hoặc chọn ID học sinh trước khi lấy ảnh.")
            return

        try:
            student_id = int(student_id_raw)
        except ValueError:
            messagebox.showerror("ID không hợp lệ", "ID học sinh phải là số nguyên.")
            return

        if not self.service.student_exists(student_id):
            messagebox.showerror("Không tìm thấy", "ID học sinh chưa tồn tại trong cơ sở dữ liệu.")
            return

        ok, msg, _saved = self.dataset_service.capture_student_faces(
            student_id=student_id,
            target_samples=120,
        )
        if not ok:
            messagebox.showerror("Lấy ảnh thất bại", msg)
            return

        db_ok, db_msg = self.service.mark_photo_sample(student_id, has_sample=True)
        self.view.photo_var.set("Có ảnh")
        self._reload_table()

        if db_ok:
            messagebox.showinfo("Thành công", f"{msg}\n{db_msg}")
        else:
            messagebox.showwarning("Hoàn tất một phần", f"{msg}\n{db_msg}")

    def on_training(self) -> None:
        ok, msg = self.training_service.train_lbph_model(output_name="classifier.xml")
        if ok:
            messagebox.showinfo("Training hoàn tất", msg)
            return
        messagebox.showerror("Training thất bại", msg)

