"""
Seed script — populates the DB with realistic demo data.
Run: python manage.py shell < seed_data.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from departments.models import Department
from employees.models import Employee, Skill

# Create admin
admin, _ = User.objects.get_or_create(username='admin', defaults={'role': 'admin', 'is_staff': True, 'is_superuser': True})
admin.set_password('admin123')
admin.first_name = 'Admin'
admin.save()

# Create departments
dept_names = ['Engineering', 'Product', 'Design', 'Marketing', 'HR', 'Finance']
depts = {name: Department.objects.get_or_create(name=name)[0] for name in dept_names}

# Seed employees
employees_data = [
    {'name': 'Arjun Mehta', 'email': 'arjun@company.com', 'position': 'Senior Backend Engineer', 'dept': 'Engineering', 'phone': '+91 98765 43210', 'skills': ['Python', 'Django', 'PostgreSQL', 'Docker', 'Redis']},
    {'name': 'Priya Sharma', 'email': 'priya@company.com', 'position': 'Product Manager', 'dept': 'Product', 'phone': '+91 98765 43211', 'skills': ['Product Strategy', 'Figma', 'Data Analysis', 'Roadmapping']},
    {'name': 'Rohan Verma', 'email': 'rohan@company.com', 'position': 'Frontend Engineer', 'dept': 'Engineering', 'phone': '+91 98765 43212', 'skills': ['React', 'TypeScript', 'Tailwind', 'GraphQL']},
    {'name': 'Sneha Patel', 'email': 'sneha@company.com', 'position': 'UI/UX Designer', 'dept': 'Design', 'phone': '+91 98765 43213', 'skills': ['Figma', 'Prototyping', 'User Research', 'Design Systems']},
    {'name': 'Vikram Singh', 'email': 'vikram@company.com', 'position': 'DevOps Engineer', 'dept': 'Engineering', 'phone': '+91 98765 43214', 'skills': ['AWS', 'Kubernetes', 'CI/CD', 'Terraform', 'Docker']},
    {'name': 'Ananya Reddy', 'email': 'ananya@company.com', 'position': 'Marketing Lead', 'dept': 'Marketing', 'phone': '+91 98765 43215', 'skills': ['SEO', 'Content Strategy', 'Analytics', 'Growth Hacking']},
    {'name': 'Kunal Joshi', 'email': 'kunal@company.com', 'position': 'Data Scientist', 'dept': 'Engineering', 'phone': '+91 98765 43216', 'skills': ['Python', 'Machine Learning', 'PyTorch', 'SQL', 'Data Viz']},
    {'name': 'Deepa Nair', 'email': 'deepa@company.com', 'position': 'HR Manager', 'dept': 'HR', 'phone': '+91 98765 43217', 'skills': ['Recruiting', 'HRIS', 'Employee Relations', 'Onboarding']},
]

for data in employees_data:
    emp, created = Employee.objects.get_or_create(email=data['email'], defaults={
        'name': data['name'],
        'position': data['position'],
        'department': depts[data['dept']],
        'phone': data['phone'],
        'bio': f"{data['name']} is a key member of the {data['dept']} team at PulseDir.",
    })
    if created:
        skills = [Skill.objects.get_or_create(name=s.lower())[0] for s in data['skills']]
        emp.skills.set(skills)
        print(f"  ✓ Created: {data['name']}")

print("\n✅ Seed complete!")
print("   Login: admin / admin123")
