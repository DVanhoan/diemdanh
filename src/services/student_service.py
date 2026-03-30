from db.database import DatabaseConnection
from models.student_model import StudentModel


class StudentService:
    def __init__(self):
        self.db = DatabaseConnection().get_connection()

    def get_all_students(self):
        cursor = self.db.cursor(dictionary=True)
        query = "SELECT * FROM student"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        students = []
        for row in records:
            student = StudentModel(
                student_id=row['Student_id'],
                dep=row.get('Dep'),
                course=row.get('course'),
                year=row.get('Year'),
                semester=row.get('Semester'),
                name=row.get('Name'),
                class_name=row.get('Class'),
                roll=row.get('Roll'),
                gender=row.get('Gender'),
                dob=row.get('Dob'),
                email=row.get('Email'),
                phone=row.get('Phone'),
                address=row.get('Address'),
                photo_sample=row.get('PhotoSample'),
            )
            students.append(student)
        return students

    def search_students(self, search_type: str, keyword: str):
        kw = (keyword or "").strip()
        if not kw:
            return self.get_all_students()

        cursor = self.db.cursor(dictionary=True)

        if search_type == "ID Học sinh":
            try:
                st_id = int(kw)
            except ValueError:
                cursor.close()
                return []
            cursor.execute("SELECT * FROM student WHERE Student_id = %s", (st_id,))
        elif search_type == "Lớp học":
            cursor.execute("SELECT * FROM student WHERE Class LIKE %s", (f"%{kw}%",))
        else:  # "Tên học sinh"
            cursor.execute("SELECT * FROM student WHERE Name LIKE %s", (f"%{kw}%",))

        records = cursor.fetchall()
        cursor.close()

        students = []
        for row in records:
            students.append(
                StudentModel(
                    student_id=row['Student_id'],
                    dep=row.get('Dep'),
                    course=row.get('course'),
                    year=row.get('Year'),
                    semester=row.get('Semester'),
                    name=row.get('Name'),
                    class_name=row.get('Class'),
                    roll=row.get('Roll'),
                    gender=row.get('Gender'),
                    dob=row.get('Dob'),
                    email=row.get('Email'),
                    phone=row.get('Phone'),
                    address=row.get('Address'),
                    photo_sample=row.get('PhotoSample'),
                )
            )
        return students

    def create_student(self, student: StudentModel):
        try:
            cursor = self.db.cursor()
            query = """INSERT INTO student
                           (Student_id, Dep, course, Year, Semester, Name, Class, Roll, Gender, Dob, Email, Phone, Address, PhotoSample)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (
                student.student_id,
                student.dep,
                student.course,
                student.year,
                student.semester,
                student.name,
                student.class_name,
                student.roll,
                student.gender,
                student.dob,
                student.email,
                student.phone,
                student.address,
                student.photo_sample,
            )

            cursor.execute(query, values)
            self.db.commit()  # Lưu thay đổi
            cursor.close()
            return True, "Thêm sinh viên thành công!"
        except Exception as e:
            return False, f"Lỗi Database: {str(e)}"

    def update_student(self, student: StudentModel):
        try:
            cursor = self.db.cursor()
            query = """UPDATE student
                       SET Dep=%s, course=%s, Year=%s, Semester=%s,
                           Name=%s, Class=%s, Roll=%s, Gender=%s, Dob=%s,
                           Email=%s, Phone=%s, Address=%s, PhotoSample=%s
                       WHERE Student_id = %s"""
            values = (
                student.dep,
                student.course,
                student.year,
                student.semester,
                student.name,
                student.class_name,
                student.roll,
                student.gender,
                student.dob,
                student.email,
                student.phone,
                student.address,
                student.photo_sample,
                student.student_id,
            )

            cursor.execute(query, values)
            self.db.commit()  # Lưu thay đổi
            cursor.close()
            return True, "Cập nhật sinh viên thành công!"
        except Exception as e:
            return False, f"Lỗi Database: {str(e)}"

    def delete_student(self, student_id):
        try:
            cursor = self.db.cursor()
            query = "DELETE FROM student WHERE Student_id = %s"
            cursor.execute(query, (student_id,))
            self.db.commit()
            cursor.close()
            return True, "Xóa sinh viên thành công!"
        except Exception as e:
            return False, f"Lỗi xóa: {str(e)}"