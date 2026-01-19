from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/complete/', views.profile_complete, name='profile_complete'),
    path('bank-detail/', views.bank_detail, name='bank_detail'),
    path('loan/apply/', views.loan_application, name='loan_application'),
    path('loan/dashboard/', views.loan_dashboard, name='loan_dashboard'),
    path('withdrawal/request/', views.withdrawal_request, name='withdrawal_request'),
    path('invite/', views.send_invite, name='send_invite'),
]
