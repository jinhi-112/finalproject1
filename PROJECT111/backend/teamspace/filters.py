import django_filters
from .models import Projects

class ProjectFilter(django_filters.FilterSet):
    title__icontains = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    description__icontains = django_filters.CharFilter(field_name='description', lookup_expr='icontains')
    tech_stack__icontains = django_filters.CharFilter(field_name='tech_stack', lookup_expr='icontains')
    recruitment_count__gte = django_filters.NumberFilter(field_name='recruitment_count', lookup_expr='gte')

    class Meta:
        model = Projects
        fields = ['title__icontains', 'description__icontains', 'tech_stack__icontains', 'recruitment_count__gte', 'is_open']
