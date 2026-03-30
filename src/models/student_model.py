
class StudentModel:

    def __init__(
            self,
            student_id,
            name,
            class_name,
            dep=None,
            course=None,
            year=None,
            semester=None,
            roll=None,
            gender=None,
            dob=None,
            email=None,
            phone=None,
            address=None,
            photo_sample=None
    ) -> None:
        self.student_id = student_id
        self.name = name
        self.class_name = class_name
        self.dep = dep
        self.course = course
        self.year = year
        self.semester = semester
        self.roll = roll
        self.gender = gender
        self.dob = dob
        self.email = email
        self.phone = phone
        self.address = address
        self.photo_sample = photo_sample