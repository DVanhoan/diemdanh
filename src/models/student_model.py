from __future__ import annotations

from src.database import Database


class StudentModel:

    def __init__(self, database: Database) -> None:
        self.database = database

    def get_all_students(self) -> list[tuple[int, str, str]]:
        query = """
            SELECT Student_id, Name, Class
            FROM Student
            ORDER BY Student_id
        """
        return self.database.execute_query(query)
