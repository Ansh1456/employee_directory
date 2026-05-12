from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('directory/', views.directory, name='directory'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('employee/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employee/add/', views.employee_create, name='employee_create'),
    path('employee/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employee/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employee/<int:pk>/restore/', views.employee_restore, name='employee_restore'),
    path('employee/<int:pk>/hard-delete/', views.employee_hard_delete, name='employee_hard_delete'),
    path('employees/archived/', views.archived_employees, name='archived_employees'),
    path('departments/', views.department_list, name='department_list'),
    path('employees/export/', views.export_csv, name='export_csv'),
    path('employees/import/', views.import_csv, name='import_csv'),
    path('employees/sample-csv/', views.sample_csv, name='sample_csv'),
]
