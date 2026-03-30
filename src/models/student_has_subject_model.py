
class StudentHasSubjectModel():
    def __init__(self, student_id: int, subject_id: int):
        self.student_id = student_id
        self.subject_id = subject_id

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'subject_id': self.subject_id
        }