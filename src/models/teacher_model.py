from __future__ import annotations


class TeacherModel:

    def __init__(
        self,
        teacher_id: int | None,
        name: str,
        phone: str,
        email: str,
        security_q: str,
        security_a: str,
        password: str,
    ) -> None:
        self.teacher_id = teacher_id
        self.name = name
        self.phone = phone
        self.email = email
        self.security_q = security_q
        self.security_a = security_a
        self.password = password

