from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

import mysql.connector
from mysql.connector import Error


@dataclass
class DatabaseConfig:

    host: str = "localhost"
    user: str = "root"
    password: str = ""
    port: int = 3306
    database: str = "attendance_system"


class Database:
    """Reusable database gateway with schema bootstrap and query helpers."""

    def __init__(self, config: Optional[DatabaseConfig] = None) -> None:
        self.config = config or DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            port=int(os.getenv("DB_PORT", "3306")),
            database=os.getenv("DB_NAME", "attendance_system"),
        )
        self._connection = None

        project_root = Path(__file__).resolve().parents[1]
        self.schema_file = project_root / "database" / "init_schema.sql"

    def connect(self, with_database: bool = True) -> None:
        """Open a MySQL connection when not already connected."""
        if self._connection and self._connection.is_connected():
            return

        connection_kwargs: dict[str, Any] = {
            "host": self.config.host,
            "user": self.config.user,
            "password": self.config.password,
            "port": self.config.port,
            "autocommit": False,
        }
        if with_database:
            connection_kwargs["database"] = self.config.database

        try:
            self._connection = mysql.connector.connect(**connection_kwargs)
        except Error as exc:
            raise ConnectionError(f"Unable to connect to MySQL: {exc}") from exc

    def close(self) -> None:
        """Close active database connection safely."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def _ensure_connected(self) -> None:
        if not self._connection or not self._connection.is_connected():
            raise RuntimeError("Database connection is not open.")

    def _read_schema_statements(self) -> list[str]:
        """Read SQL file and split it into executable statements."""
        if not self.schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_file}")

        sql_text = self.schema_file.read_text(encoding="utf-8")
        cleaned_lines: list[str] = []
        for line in sql_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("--") or not stripped:
                continue
            cleaned_lines.append(line)

        cleaned_sql = "\n".join(cleaned_lines)
        return [stmt.strip() for stmt in cleaned_sql.split(";") if stmt.strip()]

    def initialize_schema(self) -> None:
        """Execute init_schema.sql to create database, tables, and seed data."""
        self.close()
        self.connect(with_database=False)
        self._ensure_connected()

        statements = self._read_schema_statements()
        cursor = self._connection.cursor()
        try:
            for statement in statements:
                cursor.execute(statement)
            self._connection.commit()
        except Error as exc:
            self._connection.rollback()
            raise RuntimeError(f"Schema initialization failed: {exc}") from exc
        finally:
            cursor.close()
            self.close()

        self.connect(with_database=True)

    def execute_query(
        self,
        query: str,
        params: Optional[Iterable[Any]] = None,
    ) -> list[tuple[Any, ...]]:
        """Execute SELECT query and return all rows."""
        self._ensure_connected()
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except Error as exc:
            raise RuntimeError(f"Query execution failed: {exc}") from exc
        finally:
            cursor.close()

    def execute_non_query(
        self,
        query: str,
        params: Optional[Iterable[Any]] = None,
    ) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows."""
        self._ensure_connected()
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, params)
            affected = cursor.rowcount
            self._connection.commit()
            return affected
        except Error as exc:
            self._connection.rollback()
            raise RuntimeError(f"Non-query execution failed: {exc}") from exc
        finally:
            cursor.close()


def test_connection() -> bool:
    """Quick connectivity and schema initialization test."""
    db = Database()
    try:
        db.initialize_schema()
        rows = db.execute_query("SELECT DATABASE();")
        print("Connected database:", rows[0][0] if rows else "Unknown")
        return True
    except (ConnectionError, RuntimeError, FileNotFoundError, Error) as exc:
        print(f"Database test failed: {exc}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    test_connection()
