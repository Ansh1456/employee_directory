from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count

from employees.models import Employee
from departments.models import Department
from .serializers import (
    EmployeeListSerializer, EmployeeDetailSerializer, DepartmentSerializer
)


class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for employees.
    Future: add write endpoints, AI search action, presence status.
    """
    queryset = Employee.objects.filter(is_active=True).select_related('department').prefetch_related('skills')
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'position', 'skills__name']
    ordering_fields = ['name', 'department__name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EmployeeDetailSerializer
        return EmployeeListSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Flexible search endpoint.
        Future: replace with vector/semantic search.
        """
        q = request.query_params.get('q', '')
        dept = request.query_params.get('dept')
        qs = self.get_queryset()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(skills__name__icontains=q) | Q(position__icontains=q)
            ).distinct()
        if dept:
            qs = qs.filter(department_id=dept)
        serializer = EmployeeListSerializer(qs, many=True, context={'request': request})
        return Response({'results': serializer.data, 'count': qs.count()})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Dashboard stats endpoint. Future: add AI insights here."""
        return Response({
            'total_employees': Employee.objects.filter(is_active=True).count(),
            'total_departments': Department.objects.count(),
            'by_department': list(
                Department.objects.annotate(count=Count('employees')).values('name', 'count')
            ),
        })


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
