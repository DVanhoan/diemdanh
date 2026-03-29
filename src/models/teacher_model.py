from __future__ import annotations

from src.database import Database


class TeacherModel:

    def __init__(self, database: Database) -> None:
        self.database = database

    def authenticate(self, username_or_email: str, password: str) -> bool:
        query = """
            SELECT Teacher_id
            FROM Teacher
            WHERE (Email = %s OR Name = %s) AND Password = %s
            LIMIT 1
        """
        rows = self.database.execute_query(
            query,
            (username_or_email, username_or_email, password),
        )
        return len(rows) > 0
