from __future__ import annotations
from src.db.database import DatabaseConnection
from src.models.lesson_model import LessonModel


class LessonService:
    def __init__(self) -> None:
        self.db = DatabaseConnection()

    def _cursor(self):
        return self.db.get_connection().cursor(dictionary=True)

    def _query(self) -> str:
        return """
            SELECT l.Lesson_id, l.Time_start, l.Time_end, l.Date,
                   l.Teacher_id, t.Name AS teacher_name,
                   l.Subject_id, s.Subject_name
            FROM lesson l
            LEFT JOIN teacher t ON l.Teacher_id = t.Teacher_id
            LEFT JOIN subject  s ON l.Subject_id = s.Subject_id
        """

    # ── Lấy tất cả ──────────────────────────────────────────
    def get_all(self) -> list[LessonModel]:
        cursor = self._cursor()
        cursor.execute(self._query() + " ORDER BY l.Lesson_id")
        rows = cursor.fetchall()
        cursor.close()
        return self._rows_to_models(rows)

    # ── Tìm kiếm ────────────────────────────────────────────
    def search(self, field: str, keyword: str) -> list[LessonModel]:
        field_map = {
            "ID Buổi học":  "l.Lesson_id",
            "Giờ bắt đầu":  "l.Time_start",
            "Giờ kết thúc": "l.Time_end",
            "Ngày":         "l.Date",
            "ID giáo viên": "l.Teacher_id",
            "ID Môn học":   "l.Subject_id",
        }
        col = field_map.get(field, "l.Lesson_id")
        cursor = self._cursor()
        cursor.execute(
            self._query() + f" WHERE {col} LIKE %s ORDER BY l.Lesson_id",
            (f"%{keyword}%",)
        )
        rows = cursor.fetchall()
        cursor.close()
        return self._rows_to_models(rows)

    # ── Thêm mới ─────────────────────────────────────────────
    def create(self, start_time: str, end_time: str, date: str,
               teacher_id: int, subject_id: int) -> None:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lesson (Time_start, Time_end, Date, Teacher_id, Subject_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (start_time, end_time, date, teacher_id, subject_id))
        conn.commit()
        cursor.close()

    # ── Cập nhật ─────────────────────────────────────────────
    def update(self, lesson_id: int, start_time: str, end_time: str,
               date: str, teacher_id: int, subject_id: int) -> None:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE lesson
            SET Time_start=%s, Time_end=%s, Date=%s,
                Teacher_id=%s, Subject_id=%s
            WHERE Lesson_id=%s
        """, (start_time, end_time, date, teacher_id, subject_id, lesson_id))
        conn.commit()
        cursor.close()

    # ── Xóa ──────────────────────────────────────────────────
    def delete(self, lesson_id: int) -> None:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lesson WHERE Lesson_id=%s", (lesson_id,))
        conn.commit()
        cursor.close()

    # ── Helper ───────────────────────────────────────────────
    @staticmethod
    def _row_to_model(row: dict) -> LessonModel:
        return LessonModel(
            lesson_id=row["Lesson_id"],
            start_time=str(row.get("Time_start")) if row.get("Time_start") else "",
            end_time=str(row.get("Time_end"))     if row.get("Time_end")   else "",
            date=row.get("Date")                  or "",
            teacher_id=row.get("Teacher_id")      or 0,
            subject_id=row.get("Subject_id")      or 0,
            teacher_name=row.get("teacher_name")  or "",
            subject_name=row.get("Subject_name")  or "",
        )

    def _rows_to_models(self, rows: list[dict]) -> list[LessonModel]:
        return [self._row_to_model(row) for row in rows]
