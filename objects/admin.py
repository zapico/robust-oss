from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import City, Object, Measure, Event, Criteria, CustomUser, Pathway
from leaflet.admin import LeafletGeoAdmin

# Models with Geo information
@admin.register(City)
class CityAdmin(LeafletGeoAdmin):
    list_display = ('name', 'location')
@admin.register(Object)
class ObjectAdmin(LeafletGeoAdmin):
    list_display = ('name', 'description')

# Models without GEO information
admin.site.register(Measure)
admin.site.register(Pathway)
admin.site.register(Event)
admin.site.register(Criteria)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff','city')

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
            ('Additional info', {
                'fields': ('city',)
            })
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('city',)
        })
    )
admin.site.register(CustomUser, CustomUserAdmin)
