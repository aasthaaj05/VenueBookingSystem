from django.contrib import admin

# Register your models here.
from django.contrib import admin
from gymkhana.models import Venue

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('venue_name', 'building', 'capacity', 'department_incharge', 'campus')
    list_filter = ('building', 'campus', 'class_type')
    search_fields = ('venue_name', 'description', 'room_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('venue_name', 'description', 'photo_url', 'picture_urls', 'capacity')
        }),
        ('Location', {
            'fields': ('building', 'floor_number', 'room_number', 'address', 'venue_location', 'campus')
        }),
        ('Dimensions', {
            'fields': ('length', 'depth_or_height', 'area_sqm')
        }),
        ('Classification', {
            'fields': ('class_type', 'class_number', 'usage_type')
        }),
        ('Facilities', {
            'fields': ('facilities',)
        }),
        ('Management', {
            'fields': ('department_incharge', 'dept_incharge_phone', 'dept_incharge_email',
                      'dept_assistant_name1', 'dept_assistant_name2', 'venue_admin')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )