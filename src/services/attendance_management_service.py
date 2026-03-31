from __future__ import annotations

from datetime import date

from src.db.database import DatabaseConnection
from src.models.attendance_model import AttendanceModel


class AttendanceManagementService:
    def __init__(self) -> None:
        self.db = DatabaseConnection().get_connection()

    def get_all_attendance(self) -> list[AttendanceModel]:
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM attendance ORDER BY Date DESC, Time_in DESC")
        records = cursor.fetchall()
        cursor.close()
        return [AttendanceModel.from_row(r) for r in records]

    def get_attendance_by_date(self, day: str) -> list[AttendanceModel]:
        cursor = self.db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM attendance WHERE Date = %s ORDER BY Time_in DESC",
            (day,),
        )
        records = cursor.fetchall()
        cursor.close()
        return [AttendanceModel.from_row(r) for r in records]

    def get_attendance_today(self) -> list[AttendanceModel]:
        return self.get_attendance_by_date(date.today().isoformat())

    def search_attendance(self, search_type: str, keyword: str) -> list[AttendanceModel]:
        kw = (keyword or "").strip()
        if not kw:
            return self.get_all_attendance()

        cursor = self.db.cursor(dictionary=True)

        if search_type == "ID Điểm Danh":
            cursor.execute("SELECT * FROM attendance WHERE IdAttendance LIKE %s", (f"%{kw}%",))
        elif search_type == "ID Học sinh":
            try:
                st_id = int(kw)
            except ValueError:
                cursor.close()
                return []
            cursor.execute("SELECT * FROM attendance WHERE Student_id = %s", (st_id,))
        elif search_type == "Tên học sinh":
            cursor.execute("SELECT * FROM attendance WHERE Name LIKE %s", (f"%{kw}%",))
        elif search_type == "Lớp học":
            cursor.execute("SELECT * FROM attendance WHERE Class LIKE %s", (f"%{kw}%",))
        elif search_type == "Ngày":
            cursor.execute("SELECT * FROM attendance WHERE Date = %s", (kw,))
        else:
            cursor.execute("SELECT * FROM attendance WHERE IdAttendance LIKE %s", (f"%{kw}%",))

        records = cursor.fetchall()
        cursor.close()
        return [AttendanceModel.from_row(r) for r in records]

    def create_attendance(self, att: AttendanceModel):
        try:
            cursor = self.db.cursor()
            query = (
                "INSERT INTO attendance (IdAttendance, Student_id, Name, Class, Time_in, Time_out, Date, Lesson_id, AttendanceStatus) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            )
            cursor.execute(query, att.to_insert_params())
            self.db.commit()
            cursor.close()
            return True, "Thêm điểm danh thành công!"
        except Exception as e:  # noqa: BLE001
            return False, f"Lỗi Database: {e}"

    def update_attendance(self, att: AttendanceModel):
        try:
            cursor = self.db.cursor()
            query = (
                "UPDATE attendance SET Student_id=%s, Name=%s, Class=%s, Time_in=%s, Time_out=%s, Date=%s, Lesson_id=%s, AttendanceStatus=%s "
                "WHERE IdAttendance=%s"
            )
            cursor.execute(query, att.to_update_params())
            self.db.commit()
            cursor.close()
            return True, "Cập nhật điểm danh thành công!"
        except Exception as e:  # noqa: BLE001
            return False, f"Lỗi Database: {e}"

    def delete_attendance(self, attendance_id: str):
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM attendance WHERE IdAttendance = %s", (attendance_id,))
            self.db.commit()
            cursor.close()
            return True, "Xóa điểm danh thành công!"
        except Exception as e:  # noqa: BLE001
            return False, f"Lỗi xóa: {e}"
