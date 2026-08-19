from datetime import date
from math import ceil

from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Timetable, Attendance


def dashboard(request):
    today = date.today()

    day_names = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
    ]

    today_name = day_names[today.weekday()]

    # Get today's lectures
    todays_lectures = Timetable.objects.filter(
        day=today_name
    ).order_by('lecture_number')

    # Get today's attendance records
    today_records = Attendance.objects.filter(
        date=today
    )

    # Attach today's attendance status to each lecture
    attendance_map = {
        record.timetable_id: record.status
        for record in today_records
    }

    for lecture in todays_lectures:
        lecture.today_status = attendance_map.get(
            lecture.id
        )

    # Get all compulsory attendance records
    records = Attendance.objects.filter(
        timetable__compulsory=True
    ).exclude(
        status='NOT_HELD'
    )

    conducted = records.count()

    present = records.filter(
        status='PRESENT'
    ).count()

    bunked = records.filter(
        status='BUNK'
    ).count()

    # Attendance percentage
    if conducted > 0:
        percentage = (present / conducted) * 100
    else:
        percentage = 0

    # Calculate safe bunks
    if conducted > 0 and percentage >= 75:

        possible_bunks = int(
            (present / 0.75) - conducted
        )

        if possible_bunks < 0:
            possible_bunks = 0

    else:
        possible_bunks = 0

    # Calculate lectures needed
    lectures_needed = 0

    if conducted > 0 and percentage < 75:

        lectures_needed = ceil(
            (0.75 * conducted - present) / 0.25
        )

    context = {
        'today': today,
        'today_name': today_name,
        'todays_lectures': todays_lectures,

        'present': present,
        'bunked': bunked,
        'conducted': conducted,
        'percentage': round(percentage, 2),

        'possible_bunks': possible_bunks,
        'lectures_needed': lectures_needed,
    }

    return render(
        request,
        'attendance/dashboard.html',
        context
    )


@require_POST
def mark_attendance(request, timetable_id):

    timetable = Timetable.objects.get(
        id=timetable_id
    )

    status = request.POST.get('status')

    if status not in [
        'PRESENT',
        'BUNK',
        'NOT_HELD'
    ]:
        return redirect('dashboard')

    Attendance.objects.update_or_create(
        date=date.today(),
        timetable=timetable,
        defaults={
            'status': status
        }
    )

    return redirect('dashboard')


def subject_attendance(request):

    subjects = []

    all_subjects = Timetable.objects.values(
        'subject_id',
        'subject__name'
    ).distinct().order_by(
        'subject__name'
    )

    for item in all_subjects:

        subject_id = item['subject_id']
        subject_name = item['subject__name']

        records = Attendance.objects.filter(
            timetable__subject_id=subject_id,
            timetable__compulsory=True
        ).exclude(
            status='NOT_HELD'
        )

        conducted = records.count()

        present = records.filter(
            status='PRESENT'
        ).count()

        if conducted > 0:
            percentage = (present / conducted) * 100
        else:
            percentage = 0

        subjects.append({
            'name': subject_name,
            'present': present,
            'conducted': conducted,
            'percentage': round(percentage, 2),
        })

    return render(
        request,
        'attendance/subjects.html',
        {
            'subjects': subjects
        }
    )