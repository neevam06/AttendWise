from django.contrib import admin
from .models import Subject, Timetable, Attendance


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = (
        'day',
        'lecture_number',
        'start_time',
        'end_time',
        'subject',
        'teacher',
        'compulsory',
    )

    list_filter = (
        'day',
        'subject',
        'compulsory',
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'timetable',
        'status',
    )

    list_filter = (
        'date',
        'status',
    )