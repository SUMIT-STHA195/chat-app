from django.urls import path
from . import views
app_name = 'authentication'
urlpatterns = [
    path('', views.register, name="register"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('change-password/', views.change_password, name='change-password'),
]
