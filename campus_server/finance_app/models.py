from django.db import models

class FeeOrder(models.Model):
    order_id = models.CharField(primary_key=True, max_length=20)
    student_id = models.CharField(max_length=20)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_status = models.CharField(max_length=1, default='0', help_text='0未付 3已付')
    ch_id = models.CharField(max_length=20, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    pay_time = models.DateTimeField(null=True)

    class Meta:
        db_table = 'fee_order'
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
