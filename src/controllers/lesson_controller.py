from __future__ import annotations
from typing import Any
from src.services.lesson_service import LessonService
from src.views.lesson_view import lessonView

class LessonController:
    def __init__(self, app: Any, router: Any) -> None:
        self.app = app
        self.router = router
        self.view: lessonView | None = None
        self.service = LessonService()

    def build_view(self) -> lessonView:
        self.view = lessonView(
            master=self.app.root,
            on_save=self._on_save,
            on_update=self._on_update,
            on_delete=self._on_delete,
            on_refresh=self._on_refresh,
            on_search=self._on_search,
            on_back=self._on_back,
            assets_dir=self.app.assets_dir,
        )
        return self.view

    def on_show(self, **kwargs: Any) -> None:
        pass  # Load dữ liệu sau

    def _load_all(self) -> None:
            try:
                lessons = self.service.get_all()
                self.view.set_table_rows(lessons)
            except Exception as e:
                self.view.set_table_rows([])
    # --- Placeholder callbacks (làm chức năng sau) ---
    def _on_save(self, start_time, end_time, date, teacher_id, subject_id):
            if not all([start_time, end_time, date, teacher_id, subject_id]):
                return False, "Vui lòng nhập đầy đủ thông tin!"
            try:
                self.service.create(start_time, end_time, date,
                                    int(teacher_id), int(subject_id))
                self._load_all()
                return True, "Thêm buổi học thành công!"
            except ValueError:
                return False, "ID giáo viên và ID môn học phải là số!"
            except Exception as e:
                return False, f"Lỗi: {e}"

    def _on_update(self, *args):
        return True, "Chưa có chức năng"

    def _on_delete(self, *args):
        return True, "Chưa có chức năng"

    def _on_refresh(self):
        return True, "Chưa có chức năng"

    def _on_search(self, keyword: str):
        return True, ""

    def _on_back(self):
        self.router.show("dashboard")
