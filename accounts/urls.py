from django.urls import path
from form_app import views

#TEMPLATE urls
app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('user_login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name = 'logout'),
    path('forgot_password/', views.forgot_password, name = 'forgot_password'),
    path('reset_password/', views.reset_password, name = 'reset_password'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),

]
