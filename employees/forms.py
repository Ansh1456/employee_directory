from django import forms
from django.core.exceptions import ValidationError
from .models import Employee, Skill
from departments.models import Department

INPUT = 'w-full px-4 py-2.5 rounded-lg border border-gray-200 text-gray-800 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 bg-white'
INPUT_ERR = 'w-full px-4 py-2.5 rounded-lg border border-red-400 text-gray-800 text-sm focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-400 bg-white'
SELECT = 'w-full px-4 py-2.5 rounded-lg border border-gray-200 text-gray-800 text-sm focus:outline-none focus:border-indigo-500 bg-white'


def normalize_skill(name):
    return name.strip().capitalize()


class EmployeeForm(forms.ModelForm):
    skills_input = forms.CharField(
        required=False, label='Skills (comma-separated)',
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': 'e.g. Python, React, Leadership'})
    )
    create_login = forms.BooleanField(
        required=False, label='Create login account for this employee',
        widget=forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600', 'id': 'id_create_login'})
    )

    class Meta:
        model = Employee
        fields = ['name', 'email', 'phone', 'department', 'position',
                  'profile_picture', 'bio', 'joined_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT}),
            'email': forms.EmailInput(attrs={'class': INPUT}),
            'phone': forms.TextInput(attrs={'class': INPUT}),
            'department': forms.Select(attrs={'class': SELECT}),
            'position': forms.TextInput(attrs={'class': INPUT}),
            'bio': forms.Textarea(attrs={'class': INPUT, 'rows': 3}),
            'joined_date': forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['skills_input'].initial = ', '.join(
                self.instance.skills.values_list('name', flat=True)
            )
            self.fields.pop('create_login')  # hide on edit

        # Apply error styling
        for name, field in self.fields.items():
            if name in self.errors and hasattr(field.widget, 'attrs'):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '').replace(
                    'border-gray-200', 'border-red-400'
                )

    def clean_profile_picture(self):
        pic = self.cleaned_data.get('profile_picture')
        if pic and hasattr(pic, 'size'):
            if pic.size > 2 * 1024 * 1024:
                raise ValidationError('Image must be under 2MB.')
            allowed = ['image/jpeg', 'image/png', 'image/webp']
            if hasattr(pic, 'content_type') and pic.content_type not in allowed:
                raise ValidationError('Only JPEG, PNG, or WEBP images are allowed.')
        return pic

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if commit:
            if user:
                if not instance.pk:
                    instance.created_by = user
                instance.updated_by = user
            instance.save()
            # Skills - normalized
            skills_raw = self.cleaned_data.get('skills_input', '')
            skill_names = [normalize_skill(s) for s in skills_raw.split(',') if s.strip()]
            skills = [Skill.objects.get_or_create(name=n)[0] for n in skill_names]
            instance.skills.set(skills)
            # Create login account if requested
            if self.cleaned_data.get('create_login') and not instance.user:
                self._create_user_account(instance)
        return instance

    def _create_user_account(self, employee):
        from django.contrib.auth import get_user_model
        import secrets, string
        User = get_user_model()
        base = employee.email.split('@')[0]
        username = base
        n = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{n}"; n += 1
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
        user = User.objects.create_user(
            username=username, email=employee.email,
            password=password, role='employee',
            first_name=employee.name.split()[0] if employee.name else '',
        )
        employee.user = user
        employee.save(update_fields=['user'])
        employee._temp_password = password
        employee._temp_username = username


class SelfEditForm(forms.ModelForm):
    """Employees can only edit their own bio/skills/phone/photo."""
    skills_input = forms.CharField(
        required=False, label='Skills (comma-separated)',
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': 'e.g. Python, React, Leadership'})
    )

    class Meta:
        model = Employee
        fields = ['phone', 'bio', 'profile_picture']
        widgets = {
            'phone': forms.TextInput(attrs={'class': INPUT}),
            'bio': forms.Textarea(attrs={'class': INPUT, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['skills_input'].initial = ', '.join(
                self.instance.skills.values_list('name', flat=True)
            )

    def clean_profile_picture(self):
        pic = self.cleaned_data.get('profile_picture')
        if pic and hasattr(pic, 'size'):
            if pic.size > 2 * 1024 * 1024:
                raise ValidationError('Image must be under 2MB.')
        return pic

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            skills_raw = self.cleaned_data.get('skills_input', '')
            skill_names = [normalize_skill(s) for s in skills_raw.split(',') if s.strip()]
            skills = [Skill.objects.get_or_create(name=n)[0] for n in skill_names]
            instance.skills.set(skills)
        return instance


class DepartmentForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Department name'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': INPUT, 'rows': 2, 'placeholder': 'Optional description'})
    )
