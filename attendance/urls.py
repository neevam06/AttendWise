from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'mark-attendance/<int:timetable_id>/',
        views.mark_attendance,
        name='mark_attendance'
    ),
]