from django.urls import path
from .views import UserAuthLoginView, MemberAuthLoginView

urlpatterns = [
    path('userAuth/login', UserAuthLoginView.as_view()),
    path('memberAuth/login', MemberAuthLoginView.as_view()),
]
