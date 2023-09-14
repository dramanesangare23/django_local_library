from django.urls import path, include

from .views import dashboard_user, register_user

urlpatterns = [
    path('', dashboard_user, name = 'dashboard-users'),
    path('register', register_user, name = 'register-user'),

]
