from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, DepartmentViewSet

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee-api')
router.register('departments', DepartmentViewSet, basename='department-api')

urlpatterns = router.urls
