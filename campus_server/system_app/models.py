from django.db import models

class SysUser(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    dept_id = models.BigIntegerField(null=True)
    user_name = models.CharField(max_length=30, unique=True)
    user_type = models.CharField(max_length=1, default='0', help_text='0管理员 1教师 2学生')
    phone = models.CharField(max_length=11, null=True, unique=True)
    password = models.CharField(max_length=255, default='123456')
    status = models.CharField(max_length=1, default='0', help_text='0正常 1停用')
    del_flag = models.CharField(max_length=1, default='0')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sys_user'
        managed = False

class SysRole(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=30)
    role_code = models.CharField(max_length=30, help_text='role:admin/teacher/student')
    status = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'sys_role'
        managed = False

class SysRoleUser(models.Model):
    user_id = models.BigIntegerField()
    role_id = models.BigIntegerField()

    class Meta:
        db_table = 'sys_role_user'
        managed = False
        unique_together = (('user_id','role_id'),)

class SysMenu(models.Model):
    menu_id = models.BigAutoField(primary_key=True)
    parent_id = models.BigIntegerField(default=0)
    menu_name = models.CharField(max_length=50)
    path = models.CharField(max_length=200, null=True)
    icon = models.CharField(max_length=50, null=True)
    sort = models.IntegerField(default=0)

    class Meta:
        db_table = 'sys_menu'
        managed = False

class SysRoleMenu(models.Model):
    role_id = models.BigIntegerField()
    menu_id = models.BigIntegerField()

    class Meta:
        db_table = 'sys_role_menu'
        managed = False
        unique_together = (('role_id','menu_id'),)

class SysDept(models.Model):
    dept_id = models.BigAutoField(primary_key=True)
    dept_name = models.CharField(max_length=50)
    parent_id = models.BigIntegerField(null=True, default=0)
    order_num = models.IntegerField(default=0)
    status = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'sys_dept'
        managed = False

class SysDictType(models.Model):
    dict_id = models.BigAutoField(primary_key=True)
    dict_name = models.CharField(max_length=100)
    dict_type = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'sys_dict_type'
        managed = False

class SysDictData(models.Model):
    dict_code = models.BigAutoField(primary_key=True)
    dict_type = models.CharField(max_length=100)
    dict_label = models.CharField(max_length=100)
    dict_value = models.CharField(max_length=100)
    dict_sort = models.IntegerField(default=0)
    status = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'sys_dict_data'
        managed = False

class SysNotice(models.Model):
    notice_id = models.BigAutoField(primary_key=True)
    notice_title = models.CharField(max_length=100)
    notice_content = models.TextField(null=True)
    notice_type = models.CharField(max_length=1, default='1')
    status = models.CharField(max_length=1, default='0')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sys_notice'
        managed = False

class HealthNews(models.Model):
    news_id = models.CharField(primary_key=True, max_length=50)
    news_title = models.CharField(max_length=255)
    news_content = models.TextField(null=True)
    news_source = models.CharField(max_length=50, null=True)
    imag_url = models.CharField(max_length=255, null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'health_news'
        managed = False

class HosBanner(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=500, null=True)
    position = models.IntegerField(default=0)
    enabled = models.IntegerField(default=1)
    deleted = models.IntegerField(default=0)

    class Meta:
        db_table = 'hos_banner'
        managed = False

class SysLoginInfo(models.Model):
    info_id = models.BigAutoField(primary_key=True)
    user_name = models.CharField(max_length=30, null=True)
    login_account = models.CharField(max_length=11, null=True)
    ip_addr = models.CharField(max_length=50, null=True)
    login_status = models.CharField(max_length=1, default='0')
    login_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sys_login_info'
        managed = False

class SysOperLog(models.Model):
    oper_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50, null=True)
    oper_name = models.CharField(max_length=50, null=True)
    oper_url = models.CharField(max_length=255, null=True)
    oper_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sys_oper_log'
        managed = False

class SysWhiteName(models.Model):
    id = models.BigAutoField(primary_key=True)
    path = models.CharField(max_length=255)
    status = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'sys_white_name'
        managed = False
