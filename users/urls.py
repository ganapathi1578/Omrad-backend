from django.urls import path
from .views import RequestOTPView, VerifyOTPView

urlpatterns = [
    path('request-code/', RequestOTPView.as_view(), name='request-code'),
    path('verify-code/', VerifyOTPView.as_view(), name='verify-code'),
]