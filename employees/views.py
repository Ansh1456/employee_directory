import csv
import io
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Employee, Skill
from .forms import EmployeeForm, SelfEditForm, DepartmentForm
from departments.models import Department


# ── Access control ────────────────────────────────────────────────────────────

def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin_user:
            messages.error(request, "Access denied. Admin only.")
            return redirect('directory')
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    now = timezone.now()
    active = Employee.objects.filter(is_active=True, is_archived=False)
    dept_stats = Department.objects.annotate(count=Count('employees')).order_by('-count')
    top_skills = (Skill.objects.annotate(count=Count('employees'))
                  .filter(count__gt=0).order_by('-count')[:8])
    this_month = active.filter(created_at__year=now.year, created_at__month=now.month).count()
    last_month_date = date(now.year, now.month - 1 if now.month > 1 else 12, 1)
    last_month = active.filter(
        created_at__year=last_month_date.year,
        created_at__month=last_month_date.month
    ).count()
    no_skills = active.filter(skills__isnull=True).count()
    no_photo = active.filter(profile_picture='').count()
    no_phone = active.filter(phone='').count()
    return render(request, 'dashboard/index.html', {
        'total_employees': active.count(),
        'total_departments': Department.objects.count(),
        'recent_employees': active.order_by('-created_at')[:5],
        'dept_stats': dept_stats,
        'top_skills': top_skills,
        'this_month': this_month,
        'last_month': last_month,
        'no_skills': no_skills,
        'no_photo': no_photo,
        'no_phone': no_phone,
    })


# ── Directory ─────────────────────────────────────────────────────────────────

@login_required
def directory(request):
    employees = (Employee.objects
                 .filter(is_active=True, is_archived=False)
                 .select_related('department')
                 .prefetch_related('skills'))
    departments = Department.objects.all()
    query = request.GET.get('q', '').strip()
    dept_ids = request.GET.getlist('dept')

    if query:
        employees = employees.filter(
            Q(name__icontains=query) |
            Q(skills__name__icontains=query) |
            Q(position__icontains=query)
        ).distinct()
    if dept_ids:
        employees = employees.filter(department__id__in=dept_ids)

    total_all = Employee.objects.filter(is_active=True, is_archived=False).count()
    return render(request, 'employees/directory.html', {
        'employees': employees,
        'departments': departments,
        'query': query,
        'dept_ids': dept_ids,
        'total_count': employees.count(),
        'total_all': total_all,
    })


# ── Employee CRUD ─────────────────────────────────────────────────────────────

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/detail.html', {'employee': employee})


@admin_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            emp = form.save(user=request.user)
            msg = f"{emp.name} added successfully."
            if hasattr(emp, '_temp_password'):
                msg += f" Login created — username: <strong>{emp._temp_username}</strong>, temporary password: <strong>{emp._temp_password}</strong>"
            messages.success(request, msg)
            return redirect('directory')
    else:
        form = EmployeeForm()
    return render(request, 'employees/form.html', {'form': form, 'action': 'Add'})


@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    # Employees can only edit their own profile; admins can edit anyone
    if not request.user.is_admin_user:
        linked = getattr(request.user, 'employee_profile', None)
        if not linked or linked.pk != pk:
            messages.error(request, "You can only edit your own profile.")
            return redirect('employee_detail', pk=pk)
        FormClass = SelfEditForm
    else:
        FormClass = EmployeeForm

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            if FormClass == EmployeeForm:
                form.save(user=request.user)
            else:
                form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('employee_detail', pk=pk)
    else:
        form = FormClass(instance=employee)
    return render(request, 'employees/form.html', {
        'form': form, 'action': 'Edit', 'employee': employee,
        'self_edit': FormClass == SelfEditForm
    })


@admin_required
def employee_delete(request, pk):
    """Soft delete — archives instead of destroying."""
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.is_archived = True
        employee.is_active = False
        employee.updated_by = request.user
        employee.save()
        messages.success(request, f"{employee.name} has been archived.")
        return redirect('directory')
    return render(request, 'employees/confirm_delete.html', {'employee': employee})


@admin_required
def employee_restore(request, pk):
    employee = get_object_or_404(Employee, pk=pk, is_archived=True)
    if request.method == 'POST':
        employee.is_archived = False
        employee.is_active = True
        employee.updated_by = request.user
        employee.save()
        messages.success(request, f"{employee.name} has been restored.")
    return redirect('archived_employees')


@admin_required
def employee_hard_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk, is_archived=True)
    if request.method == 'POST':
        name = employee.name
        employee.delete()
        messages.success(request, f"{name} permanently deleted.")
    return redirect('archived_employees')


@admin_required
def archived_employees(request):
    employees = Employee.objects.filter(is_archived=True).select_related('department')
    return render(request, 'employees/archived.html', {'employees': employees})


@login_required
def my_profile(request):
    try:
        emp = request.user.employee_profile
        return redirect('employee_detail', pk=emp.pk)
    except Exception:
        messages.info(request, "No employee profile is linked to your account.")
        return redirect('dashboard')


# ── Departments ───────────────────────────────────────────────────────────────

@admin_required
def department_list(request):
    departments = Department.objects.annotate(count=Count('employees')).order_by('name')
    form = DepartmentForm()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            form = DepartmentForm(request.POST)
            if form.is_valid():
                dept, created = Department.objects.get_or_create(
                    name=form.cleaned_data['name'].strip(),
                    defaults={'description': form.cleaned_data.get('description', '')}
                )
                if created:
                    messages.success(request, f"Department '{dept.name}' created.")
                else:
                    messages.warning(request, f"'{dept.name}' already exists.")
                return redirect('department_list')
        elif action == 'delete':
            dept_id = request.POST.get('dept_id')
            dept = get_object_or_404(Department, pk=dept_id)
            active_count = dept.employees.filter(is_archived=False).count()
            if active_count > 0:
                messages.error(request, f"Cannot delete '{dept.name}' — it has {active_count} active employee(s). Move or archive them first.")
            else:
                dept.delete()
                messages.success(request, f"Department '{dept.name}' deleted.")
            return redirect('department_list')
        elif action == 'rename':
            dept_id = request.POST.get('dept_id')
            new_name = request.POST.get('new_name', '').strip()
            dept = get_object_or_404(Department, pk=dept_id)
            if new_name:
                dept.name = new_name
                dept.save()
                messages.success(request, f"Renamed to '{new_name}'.")
            return redirect('department_list')
    return render(request, 'departments/list.html', {
        'departments': departments, 'form': form
    })


# ── CSV Export ────────────────────────────────────────────────────────────────

@admin_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pulsedir_employees.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Department', 'Position', 'Skills', 'Joined Date', 'Active'])

    qs = Employee.objects.filter(is_archived=False).select_related('department').prefetch_related('skills')
    q = request.GET.get('q', '')
    dept_ids = request.GET.getlist('dept')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(skills__name__icontains=q) | Q(position__icontains=q)).distinct()
    if dept_ids:
        qs = qs.filter(department__id__in=dept_ids)

    for emp in qs:
        writer.writerow([
            emp.name, emp.email, emp.phone,
            emp.department.name if emp.department else '',
            emp.position,
            '; '.join(s.name for s in emp.skills.all()),
            emp.joined_date or '',
            'Yes' if emp.is_active else 'No',
        ])
    return response


# ── CSV Import ────────────────────────────────────────────────────────────────

@admin_required
def import_csv(request):
    preview = []
    error = None
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'preview' and 'csv_file' in request.FILES:
            f = request.FILES['csv_file']
            try:
                text = f.read().decode('utf-8-sig')
                reader = csv.DictReader(io.StringIO(text))
                rows = list(reader)
                preview = rows[:5]
                request.session['csv_import_data'] = rows
            except Exception as e:
                error = f"Could not parse file: {e}"
        elif action == 'confirm':
            rows = request.session.pop('csv_import_data', [])
            created, skipped = 0, 0
            for row in rows:
                email = row.get('Email', '').strip()
                if not email or Employee.objects.filter(email=email).exists():
                    skipped += 1
                    continue
                dept_name = row.get('Department', '').strip()
                dept = None
                if dept_name:
                    dept, _ = Department.objects.get_or_create(name=dept_name)
                emp = Employee.objects.create(
                    name=row.get('Name', '').strip(),
                    email=email,
                    phone=row.get('Phone', '').strip(),
                    position=row.get('Position', '').strip(),
                    department=dept,
                    created_by=request.user,
                    updated_by=request.user,
                )
                for s in row.get('Skills', '').split(';'):
                    s = s.strip().capitalize()
                    if s:
                        skill, _ = Skill.objects.get_or_create(name=s)
                        emp.skills.add(skill)
                created += 1
            messages.success(request, f"Import complete: {created} created, {skipped} skipped (duplicates or missing email).")
            return redirect('directory')
    return render(request, 'employees/import.html', {'preview': preview, 'error': error})


def sample_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pulsedir_sample.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Department', 'Position', 'Skills', 'Joined Date'])
    writer.writerow(['Jane Smith', 'jane@company.com', '+91 98765 00001', 'Engineering', 'Backend Engineer', 'Python; Django; SQL', '2024-01-15'])
    writer.writerow(['Bob Lee', 'bob@company.com', '+91 98765 00002', 'Design', 'UI Designer', 'Figma; Prototyping', '2024-03-01'])
    return response
