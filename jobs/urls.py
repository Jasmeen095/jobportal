from django.urls import path
from jobs import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/' , views.home , name = 'home'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('apply/<int:job_id>/' , views.apply_job , name = 'apply_job'),
    path('post-job/' , views.post_job , name = 'post_job'),
    path('dashboard/' , views.dashboard , name = 'dashboard'),
    path('update_status/<int:app_id>/' , views.update_status , name = 'update_status'),
    path('delete/<int:job_id>/' , views.delete_job , name = 'delete_job'),
    path('my-applications/' , views.applicant_dashboard , name = 'applicant_dashboard'),
]
