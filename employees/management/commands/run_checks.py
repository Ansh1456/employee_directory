import os, sys
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Health check: DB, media, migrations, employee count'

    def handle(self, *args, **kwargs):
        ok = True
        self.stdout.write('\n── PulseDir Health Check ──────────────────')

        # DB check
        try:
            connection.ensure_connection()
            from employees.models import Employee
            count = Employee.objects.filter(is_archived=False).count()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Database OK — {count} active employees'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Database ERROR: {e}')); ok = False

        # Media folder
        from django.conf import settings
        media = settings.MEDIA_ROOT
        if os.path.isdir(media) and os.access(media, os.W_OK):
            self.stdout.write(self.style.SUCCESS(f'  ✓ Media folder writable ({media})'))
        else:
            self.stdout.write(self.style.WARNING(f'  ! Media folder not writable: {media}')); ok = False

        # Pending migrations
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            self.stdout.write(self.style.WARNING(f'  ! {len(plan)} unapplied migration(s) — run: python manage.py migrate'))
            ok = False
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ All migrations applied'))

        # Departments
        from departments.models import Department
        dept_count = Department.objects.count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ {dept_count} department(s)'))

        self.stdout.write('────────────────────────────────────────────')
        if ok:
            self.stdout.write(self.style.SUCCESS('  All checks passed. Ready.\n'))
        else:
            self.stdout.write(self.style.ERROR('  Some checks failed. See above.\n'))
            sys.exit(1)
