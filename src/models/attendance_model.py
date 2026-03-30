from pip._internal import models


class AttendanceModel(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.IntegerField()
    student_name = models.CharField(max_length=45)
    class_name = models.CharField(max_length=45)
    timeIn = models.TimeField()
    timeOut = models.TimeField()
    date = models.CharField(max_length=45)
    lesson_id = models.IntegerField()
    status = models.CharField(max_length=45)

    class Meta:
        db_table = 'attendance'
        managed = False

