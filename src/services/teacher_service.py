from __future__ import annotations

from mysql.connector import Error

from src.db.database import DatabaseConnection
from src.models.teacher_model import TeacherModel


class TeacherService:
    def __init__(self) -> None:
        self.db = DatabaseConnection().get_connection()

    @staticmethod
    def _row_to_model(row: dict) -> TeacherModel:
        return TeacherModel(
            teacher_id=row["Teacher_id"],
            name=row["Name"],
            phone=row["Phone"],
            email=row["Email"],
            security_q=row["SecurityQ"],
            security_a=row["SecurityA"],
            password=row["Password"],
        )

    def get_all_teachers(self) -> list[TeacherModel]:
        cursor = self.db.cursor(dictionary=True)
        cursor.execute(
            "SELECT Teacher_id, Name, Phone, Email, SecurityQ, SecurityA, Password FROM teacher"
        )
        records = cursor.fetchall()
        cursor.close()
        return [self._row_to_model(row) for row in records]

    def search_teachers(self, keyword: str) -> list[TeacherModel]:
        kw = (keyword or "").strip()
        if not kw:
            return self.get_all_teachers()

        cursor = self.db.cursor(dictionary=True)

        if kw.isdigit():
            cursor.execute(
                "SELECT Teacher_id, Name, Phone, Email, SecurityQ, SecurityA, Password "
                "FROM teacher WHERE Teacher_id = %s",
                (int(kw),),
            )
            records = cursor.fetchall()
        else:
            like = f"%{kw}%"
            cursor.execute(
                "SELECT Teacher_id, Name, Phone, Email, SecurityQ, SecurityA, Password "
                "FROM teacher "
                "WHERE Name LIKE %s OR Email LIKE %s OR Phone LIKE %s",
                (like, like, like),
            )
            records = cursor.fetchall()

        cursor.close()
        return [self._row_to_model(row) for row in records]

    def create_teacher(self, teacher: TeacherModel):
        try:
            cursor = self.db.cursor()
            query = (
                "INSERT INTO teacher (Name, Phone, Email, SecurityQ, SecurityA, Password) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            values = (
                teacher.name,
                teacher.phone,
                teacher.email,
                teacher.security_q,
                teacher.security_a,
                teacher.password,
            )
            cursor.execute(query, values)
            self.db.commit()
            cursor.close()
            return True, "Thêm giảng viên thành công!"
        except Error as e:
            return False, f"Lỗi Database: {str(e)}"
        except Exception as e:  # noqa: BLE001
            return False, f"Lỗi: {str(e)}"

    def update_teacher(self, teacher: TeacherModel):
        if teacher.teacher_id is None:
            return False, "Thiếu Teacher_id để cập nhật!"
        try:
            cursor = self.db.cursor()
            query = (
                "UPDATE teacher SET Name=%s, Phone=%s, Email=%s, SecurityQ=%s, SecurityA=%s, Password=%s "
                "WHERE Teacher_id=%s"
            )
            values = (
                teacher.name,
                teacher.phone,
                teacher.email,
                teacher.security_q,
                teacher.security_a,
                teacher.password,
                teacher.teacher_id,
            )
            cursor.execute(query, values)
            self.db.commit()
            cursor.close()
            return True, "Cập nhật giảng viên thành công!"
        except Error as e:
            return False, f"Lỗi Database: {str(e)}"
        except Exception as e:  # noqa: BLE001
            return False, f"Lỗi: {str(e)}"

    def delete_teacher(self, teacher_id: int):
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM teacher WHERE Teacher_id=%s", (teacher_id,))
            self.db.commit()
            cursor.close()
            return True, "Xóa giảng viên thành công!"
        except Error as e:
            return False, f"Lỗi Database: {str(e)}"
        except Exception as e:  # noqa: BLE001
            return False, f"Lỗi: {str(e)}"

    def authenticate(self, username_or_email: str, password: str) -> bool:
        cursor = self.db.cursor(dictionary=True)
        cursor.execute(
            "SELECT Teacher_id FROM teacher WHERE (Email=%s OR Name=%s) AND Password=%s LIMIT 1",
            (username_or_email, username_or_email, password),
        )
        row = cursor.fetchone()
        cursor.close()
        return row is not None

