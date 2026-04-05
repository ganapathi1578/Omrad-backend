from django.contrib import admin
from .models import UsageLog


class UsageLogAdmin(admin.ModelAdmin):
    # Columns shown in admin list view
    list_display = (
        'user',
        'model_used',
        'prompt_tokens',
        'completion_tokens',
        'total_tokens',
        'timestamp'
    )

    # Filters (right sidebar)
    list_filter = (
        'model_used',
        'timestamp'
    )

    # Search functionality
    search_fields = (
        'user__email',
    )

    # Read-only fields (important: logs should not be editable)
    readonly_fields = (
        'user',
        'prompt_tokens',
        'completion_tokens',
        'total_tokens',
        'model_used',
        'timestamp'
    )

    # Ordering (latest first)
    ordering = ('-timestamp',)


# Register model
admin.site.register(UsageLog, UsageLogAdmin)