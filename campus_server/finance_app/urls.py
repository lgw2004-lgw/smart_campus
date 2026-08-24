from django.urls import path
from .views import FeeCalcView, FeePayMsgView, WeChatNativeCodeView, WeChatPayStatusView, FeeOrderUpdateView, FeeOrderQueryByPageView, FeeRefundView, TuitionSaveView, TuitionQueryView, TuitionGetView, TuitionPayView, RetakeFeeCalcView, RetakeEnrollView

urlpatterns = [
    path('fee/calc', FeeCalcView.as_view()),
    path('fee/payMsg', FeePayMsgView.as_view()),
    path('weChatPay/getNativeCodeUrl/<str:order_id>', WeChatNativeCodeView.as_view()),
    path('weChatPay/getPayStatus/<str:order_no>', WeChatPayStatusView.as_view()),
    path('feeOrder/updateById/<str:order_no>', FeeOrderUpdateView.as_view()),
    path('feeOrder/queryByPage', FeeOrderQueryByPageView.as_view()),
    path('fee/refund', FeeRefundView.as_view()),
    path('fee/tuition/save', TuitionSaveView.as_view()),
    path('fee/tuition/queryByPage', TuitionQueryView.as_view()),
    path('fee/tuition/get', TuitionGetView.as_view()),
    path('fee/tuition/pay', TuitionPayView.as_view()),
    path('fee/retake/calc', RetakeFeeCalcView.as_view()),
    path('fee/retake/enroll', RetakeEnrollView.as_view()),
]
