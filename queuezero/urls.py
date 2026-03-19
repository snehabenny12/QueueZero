from django.urls import path
from . import views

app_name = "queuezero"  # ✅ important for namespacing

urlpatterns = [
    # ----------------------
    # Patient URLs
    # ----------------------
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),  # optional alias
    path('my-token/', views.my_token, name='my_token'),
    path('token/generate/', views.generate_token, name='generate_token'),
    path('token/<int:token_id>/', views.token_detail, name='token_detail'),
    path('token/<int:token_id>/print/', views.token_print, name='token_print'),
    path('token/status/<int:token_id>/', views.check_token_status, name='check_token_status'),

    # ----------------------
    # Doctor URLs
    # ----------------------
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/toggle-availability/', views.toggle_availability, name='toggle_availability'),
    
    # Call next token / mark served with path parameters
  # Correct URL with token_id
   path('doctor/call-next/<int:token_id>/', views.call_next_token, name='call_next_token'),

    path('doctor/mark-served/<int:token_id>/', views.mark_served, name='mark_served'),

    # AJAX endpoint
    path('doctors-by-department/', views.doctors_by_department, name='doctors_by_department'),
]
