from __future__ import annotations


class LessonModel:
    def __init__(
        self,
        lesson_id: int,
        start_time: str,
        end_time: str,
        date: str,
        teacher_id: int,
        teacher_name: str,
        subject_id: int,
        subject_name: str,
    ) -> None:
        self.lesson_id = lesson_id
        self.start_time = start_time
        self.end_time = end_time
        self.date = date
        self.teacher_id = teacher_id
        self.teacher_name = teacher_name
        self.subject_id = subject_id
        self.subject_name = subject_name
