from __future__ import annotations
from typing import Any
from src.views.lesson_view import lessonView

class LessonController:
    def __init__(self, app: Any, router: Any) -> None:
        self.app = app
        self.router = router
        self.view: lessonView | None = None

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

    # --- Placeholder callbacks (làm chức năng sau) ---
    def _on_save(self, *args):
        return True, "Chưa có chức năng"

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
