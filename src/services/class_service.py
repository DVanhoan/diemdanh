from __future__ import annotations

from src.db.database import DatabaseConnection
from src.models.class_model import ClassModel


class ClassService:
    def __init__(self) -> None:
        self.db = DatabaseConnection().get_connection()

    def get_all_classes(self) -> list[tuple[str, str]]:
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT Class, Name FROM class ORDER BY Class")
        rows = cursor.fetchall()
        cursor.close()
        return [(str(r["Class"]), str(r["Name"])) for r in rows]

    def get_all_class_models(self) -> list[ClassModel]:
        return [ClassModel(class_id, name) for class_id, name in self.get_all_classes()]

    def get_class_id_to_name(self) -> dict[str, str]:
        return {class_id: name for class_id, name in self.get_all_classes()}

    def search_classes(self, keyword: str) -> list[tuple[str, str]]:
        kw = (keyword or "").strip()
        if not kw:
            return self.get_all_classes()

        cursor = self.db.cursor(dictionary=True)
        like = f"%{kw}%"
        cursor.execute(
            "SELECT Class, Name FROM class WHERE Class LIKE %s OR Name LIKE %s ORDER BY Class",
            (like, like),
        )
        rows = cursor.fetchall()
        cursor.close()
        return [(str(r["Class"]), str(r["Name"])) for r in rows]

    def search_class_models(self, keyword: str) -> list[ClassModel]:
        return [ClassModel(class_id, name) for class_id, name in self.search_classes(keyword)]

    def create_class(self, class_id: str, name: str):
        try:
            cursor = self.db.cursor()
            cursor.execute("INSERT INTO class (Class, Name) VALUES (%s, %s)", (class_id, name))
            self.db.commit()
            cursor.close()
            return True, "Thêm lớp học thành công!"
        except Exception as e:
            return False, f"Lỗi Database: {str(e)}"

    def update_class(self, class_id: str, name: str):
        try:
            cursor = self.db.cursor()
            cursor.execute("UPDATE class SET Name=%s WHERE Class=%s", (name, class_id))
            self.db.commit()
            cursor.close()
            return True, "Cập nhật lớp học thành công!"
        except Exception as e:
            return False, f"Lỗi Database: {str(e)}"

    def delete_class(self, class_id: str):
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM class WHERE Class=%s", (class_id,))
            self.db.commit()
            cursor.close()
            return True, "Xóa lớp học thành công!"
        except Exception as e:
            return False, f"Lỗi Database: {str(e)}"

