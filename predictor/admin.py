from django.contrib import admin

from .models import PredictionResult


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'predicted_class', 'confidence_pct', 'gender', 'age_months', 'created_at')
    list_filter = ('predicted_class', 'gender')
    ordering = ('-created_at',)
    readonly_fields = [f.name for f in PredictionResult._meta.fields]

    def has_add_permission(self, request):
        return False
