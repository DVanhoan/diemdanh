from __future__ import annotations

from src.db.database import DatabaseConnection
from src.models.class_model import ClassModel


class ClassService:
    def __init__(self) -> None:
        self.db = DatabaseConnection().get_connection()

    @staticmethod
    def _row_to_model(row: dict) -> ClassModel:
        return ClassModel(str(row["Class"]), str(row["Name"]))

    def _fetch_classes(self, where_clause: str = "", params: tuple = ()) -> list[ClassModel]:
        cursor = self.db.cursor(dictionary=True)
        query = "SELECT Class, Name FROM class"
        if where_clause:
            query = f"{query} {where_clause}"
        query = f"{query} ORDER BY Class"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return [self._row_to_model(r) for r in rows]

    def get_all_classes(self) -> list[ClassModel]:
        return self._fetch_classes()

    def get_class_id_to_name(self) -> dict[str, str]:
        return {class_model.class_id: class_model.name for class_model in self.get_all_classes()}

    def search_classes(self, keyword: str) -> list[ClassModel]:
        kw = (keyword or "").strip()
        if not kw:
            return self.get_all_classes()

        like = f"%{kw}%"
        return self._fetch_classes("WHERE Class LIKE %s OR Name LIKE %s", (like, like))

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

