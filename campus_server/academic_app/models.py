from django.db import models

class StuStudent(models.Model):
    student_id = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=30)
    sex = models.CharField(max_length=1, null=True)
    id_card = models.CharField(max_length=18, unique=True, null=True)
    phone = models.CharField(max_length=11, null=True)
    dept_id = models.BigIntegerField(null=True)
    class_id = models.BigIntegerField(null=True)
    enroll_year = models.IntegerField(null=True)
    is_final = models.CharField(max_length=1, default='0')
    avatar = models.CharField(max_length=255, null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stu_student'
        managed = False

class StuStudentFile(models.Model):
    student_id = models.CharField(primary_key=True, max_length=20)
    family_info = models.TextField(null=True)
    health_info = models.TextField(null=True)
    award_punish = models.TextField(null=True)
    remark = models.TextField(null=True)
    emergency_contact = models.CharField(max_length=30, null=True)
    emergency_phone = models.CharField(max_length=20, null=True)
    update_time = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'stu_student_file'
        managed = False

class StuClass(models.Model):
    class_id = models.BigAutoField(primary_key=True)
    class_name = models.CharField(max_length=50)
    dept_id = models.BigIntegerField(null=True)
    grade = models.IntegerField(null=True)
    head_teacher_id = models.BigIntegerField(null=True)

    class Meta:
        db_table = 'stu_class'
        managed = False

class AcaCourse(models.Model):
    course_id = models.CharField(primary_key=True, max_length=20)
    course_name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=20, unique=True)
    credit = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    hours = models.IntegerField(null=True)
    dept_id = models.BigIntegerField(null=True)
    course_type = models.CharField(max_length=20, null=True, verbose_name='课程类型')
    status = models.CharField(max_length=1, default='0')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'aca_course'
        managed = False

class AcaScheduling(models.Model):
    id = models.BigAutoField(primary_key=True)
    course_id = models.CharField(max_length=20, null=True)
    teacher_id = models.BigIntegerField(null=True)
    classroom_id = models.BigIntegerField(null=True)
    scheduling_day = models.DateField(null=True)
    section_type = models.CharField(max_length=4, default='1')
    scheduling_type = models.CharField(max_length=1, default='1')
    semester = models.CharField(max_length=20, null=True)
    weekday = models.IntegerField(null=True)
    start_week = models.IntegerField(null=True)
    end_week = models.IntegerField(null=True)
    major_id = models.BigIntegerField(null=True)
    capacity = models.IntegerField(null=True)
    is_published = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'aca_scheduling'
        managed = False

class AcaClassroom(models.Model):
    classroom_id = models.BigAutoField(primary_key=True)
    college_id = models.BigIntegerField(null=True)
    room_no = models.CharField(max_length=20)
    floor = models.IntegerField(null=True)
    capacity = models.IntegerField(default=50)

    class Meta:
        db_table = 'aca_classroom'
        managed = False
        unique_together = (('room_no',),)

class AcaPlan(models.Model):
    plan_id = models.BigAutoField(primary_key=True)
    major_id = models.BigIntegerField(null=True)
    course_id = models.CharField(max_length=20, null=True)
    year_no = models.IntegerField(default=1)
    term = models.IntegerField(default=1)
    is_required = models.CharField(max_length=1, default='1')
    credit = models.DecimalField(max_digits=3, decimal_places=1, null=True)

    class Meta:
        db_table = 'aca_plan'
        managed = False
        unique_together = (('major_id','course_id'),)

class AcaEnrollment(models.Model):
    enroll_id = models.CharField(primary_key=True, max_length=20)
    student_id = models.CharField(max_length=20)
    course_id = models.CharField(max_length=20)
    schedule_id = models.BigIntegerField(null=True)
    status = models.CharField(max_length=1, default='0')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'aca_enrollment'
        managed = False

class AcaExam(models.Model):
    exam_id = models.CharField(primary_key=True, max_length=20)
    course_id = models.CharField(max_length=20, null=True)
    exam_name = models.CharField(max_length=100)
    exam_time = models.DateTimeField(null=True)
    paper_id = models.BigIntegerField(null=True)
    status = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'aca_exam'
        managed = False

class AcaScore(models.Model):
    score_id = models.CharField(primary_key=True, max_length=20)
    student_id = models.CharField(max_length=20)
    course_id = models.CharField(max_length=20)
    exam_id = models.CharField(max_length=20, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    gpa_point = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    semester = models.CharField(max_length=20, null=True)
    exam_type = models.CharField(max_length=1, default='0', help_text='0正常 1补考 2重修')
    is_retake = models.CharField(max_length=1, default='0', help_text='0首考 1补考/重修')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'aca_score'
        managed = False
        unique_together = (('student_id','course_id','semester','exam_type'),)

class AcaAttendance(models.Model):
    id = models.BigAutoField(primary_key=True)
    student_id = models.CharField(max_length=20)
    course_id = models.CharField(max_length=20, null=True)
    schedule_id = models.BigIntegerField(null=True)
    attend_status = models.CharField(max_length=1, default='1', help_text='1到课 0缺勤')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'aca_attendance'
        managed = False
