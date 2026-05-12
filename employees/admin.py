from django.contrib import admin
from .models import Employee, Skill

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'department', 'email', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['name', 'email', 'position']
    filter_horizontal = ['skills']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ['name']
