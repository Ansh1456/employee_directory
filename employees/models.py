from django.db import models
from django.conf import settings
from departments.models import Department
from PIL import Image
import os


def profile_pic_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    username = instance.user.username if instance.user else f"emp_{instance.pk or 'new'}"
    return f'profile_pics/{username}.{ext}'


class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        null=True, blank=True,
    )
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employees',
    )
    position = models.CharField(max_length=100)
    skills = models.ManyToManyField(Skill, blank=True, related_name='employees')
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True, blank=True,
    )
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    joined_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employees_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employees_updated',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} — {self.position}"

    def get_skills_display(self):
        return [s.name for s in self.skills.all()]

    def get_initials(self):
        parts = self.name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        return self.name[:2].upper()

    @property
    def profile_completion_percentage(self):
        fields = [self.name, self.email, self.phone, self.department, self.position, self.profile_picture, self.bio]
        completed = sum(1 for f in fields if f)
        if self.skills.exists():
            completed += 1
        return int((completed / 8) * 100)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_picture:
            try:
                img_path = self.profile_picture.path
                with Image.open(img_path) as img:
                    if img.width > 400 or img.height > 400:
                        img.thumbnail((400, 400), Image.LANCZOS)
                        img.save(img_path)
            except Exception:
                pass
