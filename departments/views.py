from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Department


def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin_user:
            messages.error(request, "Admin access required.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 bg-white'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-indigo-500 bg-white resize-none', 'rows': 2}),
        }


@admin_required
def department_list(request):
    form = DepartmentForm()
    if request.method == 'POST' and 'add' in request.POST:
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Department '{form.cleaned_data['name']}' created.")
            return redirect('department_list')
    departments = Department.objects.annotate_employee_count()
    return render(request, 'departments/list.html', {'departments': departments, 'form': form})


@admin_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated.")
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'departments/edit.html', {'form': form, 'dept': dept})


@admin_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        active_count = dept.employees.filter(is_archived=False).count()
        if active_count > 0:
            messages.error(request, f"Cannot delete '{dept.name}' — it has {active_count} active employee(s). Archive or move them first.")
        else:
            dept.delete()
            messages.success(request, f"Department '{dept.name}' deleted.")
    return redirect('department_list')
