from django.db import models

class ResBuilding(models.Model):
    building_id = models.BigAutoField(primary_key=True)
    building_name = models.CharField(max_length=50)
    dept_id = models.BigIntegerField(null=True)
    floors = models.IntegerField(default=0)
    status = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'res_building'
        managed = False

class ResRoom(models.Model):
    room_id = models.BigAutoField(primary_key=True)
    building_id = models.BigIntegerField()
    room_no = models.CharField(max_length=20)
    capacity = models.IntegerField(default=4)
    occupied = models.IntegerField(default=0)
    status = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'res_room'
        managed = False

class ResDormAssign(models.Model):
    assign_id = models.CharField(primary_key=True, max_length=20)
    student_id = models.CharField(max_length=20, unique=True)
    building_id = models.BigIntegerField()
    room_id = models.BigIntegerField()
    bed_no = models.IntegerField(null=True)
    status = models.CharField(max_length=1, default='0')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'res_dorm_assign'
        managed = False

class ResDormPublish(models.Model):
    publish_id = models.BigAutoField(primary_key=True)
    college_id = models.BigIntegerField(null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    is_published = models.CharField(max_length=1, default='0')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'res_dorm_publish'
        managed = False

class ResBook(models.Model):
    book_id = models.BigAutoField(primary_key=True)
    book_name = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True, null=True)
    author = models.CharField(max_length=100, null=True)
    category = models.CharField(max_length=50, null=True)
    stock = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    del_flag = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'res_book'
        managed = False

class ResBorrow(models.Model):
    borrow_id = models.CharField(primary_key=True, max_length=20)
    student_id = models.CharField(max_length=20)
    book_id = models.BigIntegerField()
    borrow_time = models.DateTimeField(auto_now_add=True)
    return_time = models.DateTimeField(null=True)
    due_time = models.DateTimeField(null=True)
    status = models.CharField(max_length=1, default='0')
    fine = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        db_table = 'res_borrow'
        managed = False
