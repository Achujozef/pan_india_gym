import django_filters
from .models import * 

class CommonDietPlanFilter(django_filters.FilterSet):
   
    class Meta:
        model = CommonDietPlan
        fields = ['goal']
        exclude = [ 'day','breakfast','snack_mrng','lunch','snack','dinner','optional_beverages']