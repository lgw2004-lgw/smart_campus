from django.urls import path
from .views import FeeCalcView, FeePayMsgView, WeChatNativeCodeView, WeChatPayStatusView, FeeOrderUpdateView, FeeOrderQueryByPageView, FeeRefundView, TuitionSaveView, TuitionQueryView, TuitionGetView, TuitionPayView, RetakeFeeCalcView, RetakeEnrollView, CardAccountView, CardRechargeView, CardConsumeView, CardTxQueryByPageView, CardAccountsAdminView, FeeOrderExportView

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

    path('card/account', CardAccountView.as_view()),
    path('card/recharge', CardRechargeView.as_view()),
    path('card/consume', CardConsumeView.as_view()),
    path('card/tx/queryByPage', CardTxQueryByPageView.as_view()),
    path('card/accounts/queryByPage', CardAccountsAdminView.as_view()),
    path('feeOrder/export', FeeOrderExportView.as_view()),
]
