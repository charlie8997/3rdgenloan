from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/complete/', views.profile_complete, name='profile_complete'),
    path('bank-detail/', views.bank_detail, name='bank_detail'),
    path('loan/apply/', views.loan_application, name='loan_application'),
    path('loan/dashboard/', views.loan_dashboard, name='loan_dashboard'),
    path('withdrawal/request/', views.withdrawal_request, name='withdrawal_request'),
    path('terms/', views.terms, name='terms'),
    path('loan/<int:loan_id>/agreement/', views.loan_agreement, name='loan_agreement'),
    path('loan/agreement/<int:agreement_id>/download/', views.agreement_download, name='agreement_download'),
    path('loan/agreement/<int:agreement_id>/view/', views.agreement_view, name='agreement_view'),
]
