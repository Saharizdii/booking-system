from django.contrib import admin

from .models import Appointment, Service, Stylist, WorkingHours


class WorkingHoursInline(admin.TabularInline):
    model = WorkingHours
    extra = 7


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_minutes", "max_parallel", "price", "deposit_amount")


@admin.register(Stylist)
class StylistAdmin(admin.ModelAdmin):
    list_display = ("name",)
    filter_horizontal = ("services",)
    inlines = [WorkingHoursInline]


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ("stylist", "weekday", "start_time", "end_time")
    list_filter = ("stylist",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "phone",
        "stylist",
        "service",
        "date",
        "start_time",
        "status",
    )
    list_filter = ("status", "stylist", "date")
    search_fields = ("first_name", "last_name", "phone")