from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from departments.models import Department
from employees.models import Employee, Skill


def make_admin():
    return User.objects.create_user('admin_t', password='pass', role='admin', is_staff=True)

def make_employee_user():
    return User.objects.create_user('emp_t', password='pass', role='employee')

def make_dept():
    return Department.objects.get_or_create(name='Engineering')[0]

def make_emp(name='Test Person', email='test@co.com', dept=None):
    return Employee.objects.create(name=name, email=email, position='Dev', department=dept)


class AccessControlTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.emp_user = make_employee_user()
        self.dept = make_dept()
        self.emp = make_emp(dept=self.dept)

    def test_non_admin_cannot_access_add(self):
        self.client.login(username='emp_t', password='pass')
        r = self.client.get(reverse('employee_create'))
        self.assertRedirects(r, reverse('directory'))

    def test_non_admin_cannot_access_delete(self):
        self.client.login(username='emp_t', password='pass')
        r = self.client.get(reverse('employee_delete', args=[self.emp.pk]))
        self.assertRedirects(r, reverse('directory'))

    def test_employee_cannot_edit_another(self):
        other = make_emp(name='Other', email='other@co.com')
        self.emp_user.employee_profile = self.emp
        self.client.login(username='emp_t', password='pass')
        r = self.client.get(reverse('employee_edit', args=[other.pk]))
        self.assertEqual(r.status_code, 302)


class SoftDeleteTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.emp = make_emp()

    def test_archive_hides_from_directory(self):
        self.client.login(username='admin_t', password='pass')
        self.client.post(reverse('employee_delete', args=[self.emp.pk]))
        self.emp.refresh_from_db()
        self.assertTrue(self.emp.is_archived)
        r = self.client.get(reverse('directory'))
        self.assertNotContains(r, f'href="/employee/{self.emp.pk}/"')

    def test_archived_exists_in_db(self):
        self.emp.is_archived = True; self.emp.save()
        self.assertTrue(Employee.objects.filter(pk=self.emp.pk, is_archived=True).exists())

    def test_archived_appears_in_archive_list(self):
        self.emp.is_archived = True; self.emp.save()
        self.client.login(username='admin_t', password='pass')
        r = self.client.get(reverse('archived_employees'))
        self.assertContains(r, self.emp.name)


class SearchTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        skill, _ = Skill.objects.get_or_create(name='Python')
        emp = make_emp(name='Alice Dev', email='alice@co.com')
        emp.skills.add(skill)

    def test_search_by_skill(self):
        self.client.login(username='admin_t', password='pass')
        r = self.client.get(reverse('directory') + '?q=python')
        self.assertContains(r, 'Alice Dev')

    def test_search_no_match(self):
        self.client.login(username='admin_t', password='pass')
        r = self.client.get(reverse('directory') + '?q=xyznotfound')
        self.assertNotContains(r, 'Alice Dev')


class CSVExportTests(TestCase):
    def setUp(self):
        self.admin = make_admin()

    def test_export_returns_200(self):
        self.client.login(username='admin_t', password='pass')
        r = self.client.get(reverse('export_csv'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('text/csv', r['Content-Type'])
        self.assertIn('attachment', r['Content-Disposition'])
