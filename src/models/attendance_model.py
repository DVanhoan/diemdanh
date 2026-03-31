from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Any, Mapping


@dataclass(slots=True)
class AttendanceModel:
    attendance_id: str
    student_id: int
    name: str | None = None
    class_name: str | None = None
    time_in: time | str | None = None
    time_out: time | str | None = None
    date: date | str | None = None
    lesson_id: int | None = None
    attendance_status: str | None = None

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "AttendanceModel":
        return AttendanceModel(
            attendance_id=str(row.get("IdAttendance") or ""),
            student_id=int(row.get("Student_id") or 0),
            name=row.get("Name"),
            class_name=row.get("Class"),
            time_in=row.get("Time_in"),
            time_out=row.get("Time_out"),
            date=row.get("Date"),
            lesson_id=row.get("Lesson_id"),
            attendance_status=row.get("AttendanceStatus"),
        )

    def to_insert_params(self) -> tuple[Any, ...]:
        return (
            self.attendance_id,
            self.student_id,
            self.name,
            self.class_name,
            self.time_in,
            self.time_out,
            self.date,
            self.lesson_id,
            self.attendance_status,
        )

    def to_update_params(self) -> tuple[Any, ...]:
        return (
            self.student_id,
            self.name,
            self.class_name,
            self.time_in,
            self.time_out,
            self.date,
            self.lesson_id,
            self.attendance_status,
            self.attendance_id,
        )

