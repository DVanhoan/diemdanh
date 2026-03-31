from __future__ import annotations

from datetime import date
from typing import Any

from src.models.attendance_model import AttendanceModel
from src.services.attendance_service import AttendanceService
from src.views.attendance_view import AttendanceView


class AttendanceController:

    def __init__(self, app: Any, router: Any):
        self.app = app
        self.router = router
        self.service = AttendanceService()
        self.view: AttendanceView | None = None

    def build_view(self) -> AttendanceView:
        self.view = AttendanceView(
            self.app.root,
            on_update=self.on_update,
            on_delete=self.on_delete,
            on_refresh=self.on_refresh,
            on_search=self.on_search,
            on_export_csv=self.on_export_csv,
            on_import_csv=self.on_import_csv,
            on_today=self.on_today,
            on_all=self.on_all,
            on_back=self.on_back,
            assets_dir=self.app.assets_dir
        )
        return self.view

    def on_show(self, **_: object) -> None:
        self._reload_all()

    def on_back(self) -> None:
        self.router.show("dashboard")

    def _reload_all(self) -> None:
        rows = self.service.get_all_attendance()
        if self.view is not None:
            self.view.set_table_rows(rows)

    def on_refresh(self) -> tuple[bool, str]:
        self._reload_all()
        return True, "Đã làm mới danh sách."

    def on_today(self) -> tuple[bool, str]:
        rows = self.service.get_attendance_today()
        if self.view is not None:
            self.view.set_table_rows(rows)
        return True, f"Hôm nay: {len(rows)} bản ghi ({date.today().isoformat()})."

    def on_all(self) -> tuple[bool, str]:
        self._reload_all()
        return True, "Đang hiển thị tất cả."

    def on_search(self, search_type: str, keyword: str) -> tuple[bool, str]:
        rows = self.service.search_attendance(search_type, keyword)
        if self.view is not None:
            self.view.set_table_rows(rows)
        return True, f"Tìm thấy {len(rows)} kết quả."

    def on_update(
        self,
        attendance_id: str,
        student_id: str,
        name: str,
        class_name: str,
        time_in: str,
        time_out: str,
        day: str,
        lesson_id: str,
        status: str,
    ) -> tuple[bool, str]:
        att_id = (attendance_id or "").strip()
        if not att_id:
            return False, "Chưa chọn Id điểm danh để cập nhật."

        st = (student_id or "").strip()
        if not st:
            return False, "Student_id không được để trống."
        try:
            st_id_int = int(st)
        except ValueError:
            return False, "Student_id phải là số."

        lesson = (lesson_id or "").strip()
        lesson_id_int = None
        if lesson:
            try:
                lesson_id_int = int(lesson)
            except ValueError:
                return False, "Lesson_id phải là số."

        updated = AttendanceModel(
            attendance_id=att_id,
            student_id=st_id_int,
            name=(name or "").strip() or None,
            class_name=(class_name or "").strip() or None,
            time_in=(time_in or "").strip() or None,
            time_out=(time_out or "").strip() or None,
            date=(day or "").strip() or None,
            lesson_id=lesson_id_int,
            attendance_status=(status or "").strip() or None,
        )
        ok, msg = self.service.update_attendance(updated)
        if ok:
            self._reload_all()
        return ok, msg

    def on_delete(self, attendance_id: str) -> tuple[bool, str]:
        att_id = (attendance_id or "").strip()
        if not att_id:
            return False, "Chưa chọn điểm danh để xóa."
        ok, msg = self.service.delete_attendance(att_id)
        if ok:
            self._reload_all()
        return ok, msg

    def on_export_csv(self) -> tuple[bool, str]:
        # TODO: optional - depends on UI workflow.
        return False, "Chức năng Export CSV chưa được nối."

    def on_import_csv(self) -> tuple[bool, str]:
        # TODO: optional - depends on UI workflow.
        return False, "Chức năng Import CSV chưa được nối."

