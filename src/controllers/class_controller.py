from __future__ import annotations


from src.models.class_model import ClassModel
from src.services.class_service import ClassService


class ClassController:
    """Controller for managing classes.

    Even though the Class view is embedded inside StudentView, having a controller
    makes logic testable and keeps StudentController smaller.
    """

    def __init__(self) -> None:
        self.service = ClassService()

    def list_all(self) -> list[ClassModel]:
        return self.service.get_all_class_models()

    def search(self, keyword: str) -> list[ClassModel]:
        return self.service.search_class_models(keyword)

    def create(self, class_id: str, name: str):
        class_id = (class_id or "").strip()
        name = (name or "").strip()
        if not class_id or not name:
            return False, "Vui lòng nhập đủ Lớp học và Tên lớp học!"
        return self.service.create_class(class_id, name)

    def update(self, class_id: str, name: str):
        class_id = (class_id or "").strip()
        name = (name or "").strip()
        if not class_id or not name:
            return False, "Vui lòng nhập đủ Lớp học và Tên lớp học!"
        return self.service.update_class(class_id, name)

    def delete(self, class_id: str):
        class_id = (class_id or "").strip()
        if not class_id:
            return False, "Chưa chọn lớp để xóa!"
        return self.service.delete_class(class_id)


