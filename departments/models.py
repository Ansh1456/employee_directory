from django.db import models
from django.db.models import Count


class DepartmentQuerySet(models.QuerySet):
    def annotate_employee_count(self):
        return self.annotate(count=Count('employees'))


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DepartmentQuerySet.as_manager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def employee_count(self):
        return self.employees.filter(is_archived=False).count()
