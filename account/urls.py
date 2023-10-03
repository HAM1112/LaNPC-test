from django.urls import path
from . import views

urlpatterns = [
    path('' , views.signUp , name='acc-signup'),
    path('signin/' , views.signIn , name='acc-signin'),
    
    path('verify_otp/' , views.verifyOtp , name='verify-otp'),
    
    # payment urls   
    path('payment/<int:packId>/' , views.payment , name='payment' ),
    path('payment-completed/' , views.payment_completed_view , name='payment-completed' ),
    path('payment-failed/' , views.payment_failed_view , name='payment-failed' ),
]