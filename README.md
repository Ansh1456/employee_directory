# PulseDir — Employee Internal Directory System

A clean, scalable Django application. Base version — future-ready for AI search, chat, and calling.

## Quick Start

```bash
pip install django djangorestframework pillow
python manage.py migrate
python manage.py shell < seed_data.py
python manage.py runserver
```

Open: http://127.0.0.1:8000
Login: **admin / admin123**

---

## Project Architecture

```
employee_directory/
│
├── core/               # Django project settings + URL router
│   ├── settings.py     # All config; future AI/Redis/Celery hooks commented in
│   └── urls.py         # Central URL registry
│
├── users/              # Auth layer
│   ├── models.py       # Custom User with Role (admin/employee)
│   ├── forms.py        # Styled login form
│   └── views.py        # Login/Logout views
│
├── departments/        # Department management
│   └── models.py       # Department model with employee_count property
│
├── employees/          # Core feature app
│   ├── models.py       # Employee + Skill models
│   ├── forms.py        # Add/Edit form with skill parsing
│   └── views.py        # Directory, detail, CRUD, dashboard
│
├── api/                # REST API layer (DRF)
│   ├── serializers.py  # List + Detail serializers
│   ├── views.py        # ViewSets + /search and /stats endpoints
│   └── urls.py         # Router: /api/v1/employees/, /api/v1/departments/
│
└── templates/
    ├── base/layout.html    # Sidebar + navbar shell
    ├── auth/login.html     # Dark login page
    ├── dashboard/index.html
    └── employees/
        ├── directory.html  # Card grid + live JS filter
        ├── detail.html     # Full profile page
        ├── form.html       # Add/Edit form
        └── confirm_delete.html

```

---

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/employees/` | List all employees |
| GET | `/api/v1/employees/{id}/` | Employee detail |
| GET | `/api/v1/employees/search/?q=python&dept=1` | Search employees |
| GET | `/api/v1/employees/stats/` | Dashboard stats |
| GET | `/api/v1/departments/` | List departments |

---

## Future Module Integration Points

### AI Search
- Replace `api/views.py → EmployeeViewSet.search()` with vector search
- Add `ai_search/` app with embedding pipeline
- `employees/models.py → Employee` has skills M2M ready for vectorization

### Chat (WebSocket)
- Add `channels` + `channels_redis` to `INSTALLED_APPS`
- Uncomment `CHANNEL_LAYERS` in `settings.py`
- Create `chat/` app with consumers and routing
- `Employee` model has commented `availability_status` field ready

### Calling (VoIP)
- Add Twilio/WebRTC integration in new `calling/` app
- Connect to employee phone field already present in model

### Notifications
- Uncomment Celery config in `settings.py`
- Create `notifications/` app
- Hook into employee model `post_save` signals

---

## Roles

| Role | Can Do |
|------|--------|
| Admin | All CRUD, dashboard, directory |
| Employee | View directory + detail pages only |
