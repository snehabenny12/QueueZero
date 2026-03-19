from django.urls import path
from . import views

app_name = "hospital"

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.patient_register, name='patient_register'),  # name must match 'register'
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('generate-token/', views.generate_token, name='generate_token'),
    path('patient/home/', views.patient_redirect, name='patient_redirect'),
    path('about/', views.about, name='about'), 
]
