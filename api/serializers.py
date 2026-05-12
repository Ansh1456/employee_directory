from rest_framework import serializers
from employees.models import Employee, Skill
from departments.models import Department


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.ReadOnlyField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'employee_count']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list/search views."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    initials = serializers.CharField(source='get_initials', read_only=True)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'name', 'email', 'phone', 'position',
            'department_name', 'skills', 'initials',
            'profile_picture_url', 'is_active',
        ]

    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None


class EmployeeDetailSerializer(EmployeeListSerializer):
    """Full serializer for detail view."""
    department = DepartmentSerializer(read_only=True)

    class Meta(EmployeeListSerializer.Meta):
        fields = EmployeeListSerializer.Meta.fields + ['bio', 'joined_date', 'created_at', 'department']
