from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer


class CustomerAdmin(UserAdmin):
    model = Customer

    # Fields shown in list page
    list_display = (
        'email',
        'is_staff',
        'is_active',
        'daily_credits_remaining',
        'created_at'
    )

    list_filter = ('is_staff', 'is_active')

    # ✅ Make non-editable fields readonly
    readonly_fields = ('last_credit_reset', 'created_at')

    # Fields in detail (edit) view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),

        ('Credits Info', {
            'fields': ('daily_credits_remaining', 'last_credit_reset')
        }),

        ('Permissions', {
            'fields': (
                'is_staff',
                'is_active',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),

        ('Important Dates', {
            'fields': ('created_at',)
        }),
    )

    # Fields when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'is_staff',
                'is_active'
            ),
        }),
    )

    search_fields = ('email',)
    ordering = ('email',)


# Register model
admin.site.register(Customer, CustomerAdmin)