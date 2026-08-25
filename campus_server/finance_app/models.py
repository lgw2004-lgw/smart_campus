from django.db import models

class FeeOrder(models.Model):
    order_id = models.CharField(primary_key=True, max_length=20)
    student_id = models.CharField(max_length=20)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_status = models.CharField(max_length=1, default='0', help_text='0未付 3已付')
    ch_id = models.CharField(max_length=255, null=True)
    order_type = models.CharField(max_length=20, default='NORMAL', help_text='NORMAL/TUITION/RETAKE')
    semester = models.CharField(max_length=20, null=True)
    detail = models.TextField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    pay_time = models.DateTimeField(null=True)

    class Meta:
        db_table = 'fee_order'
        managed = False

class FeeTuitionConfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    semester = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    detail = models.TextField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_tuition_config'
        managed = False

class FeeOrderItem(models.Model):
    item_id = models.CharField(primary_key=True, max_length=20)
    order_id = models.CharField(max_length=20)
    ref_id = models.CharField(max_length=20, help_text='enroll_id/book_id')
    item_name = models.CharField(max_length=100, null=True)
    item_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    item_num = models.IntegerField(default=1)
    item_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'fee_order_item'
        managed = False

class FeeRefund(models.Model):
    refund_id = models.CharField(primary_key=True, max_length=20)
    order_id = models.CharField(max_length=20)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_status = models.CharField(max_length=1, default='0')
    reason = models.CharField(max_length=255, null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_refund'
        managed = False


class FinCardAccount(models.Model):
    student_id = models.CharField(primary_key=True, max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    update_time = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'fin_card_account'
        managed = False

class FinCardTransaction(models.Model):
    tx_id = models.CharField(primary_key=True, max_length=20)
    student_id = models.CharField(max_length=20)
    tx_type = models.CharField(max_length=1, help_text='1充值 2消费 3退款')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    scene = models.CharField(max_length=30, null=True)
    ref_id = models.CharField(max_length=20, null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fin_card_transaction'
        managed = False
