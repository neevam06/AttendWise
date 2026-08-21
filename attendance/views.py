from datetime import datetime
from math import ceil

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Semester, Timetable, Attendance


# =========================================================
# DASHBOARD
# =========================================================

def dashboard(request):

    # =====================================================
    # CURRENT DATE
    # =====================================================

    today = timezone.localdate()

    # =====================================================
    # SELECTED DATE
    # =====================================================

    selected_date_text = request.GET.get("date")

    selected_date = today

    if selected_date_text:

        try:
            selected_date = datetime.strptime(
                selected_date_text,
                "%Y-%m-%d"
            ).date()

        except (ValueError, TypeError):

            selected_date = today

    # =====================================================
    # PREVENT FUTURE DATE
    # =====================================================

    if selected_date > today:
        selected_date = today

    selected_day_name = selected_date.strftime("%A")

    # =====================================================
    # ACTIVE SEMESTER
    # =====================================================

    semester = Semester.objects.filter(
        active=True
    ).order_by(
        "-start_date"
    ).first()

    # =====================================================
    # SELECTED DATE LECTURES
    # =====================================================

    selected_lectures = list(
        Timetable.objects.filter(
            day=selected_day_name
        ).select_related(
            "subject"
        ).order_by(
            "lecture_number"
        )
    )

    # =====================================================
    # SELECTED DATE ATTENDANCE
    # =====================================================

    selected_attendance = {
        record.timetable_id: record.status
        for record in Attendance.objects.filter(
            date=selected_date
        )
    }

    # =====================================================
    # ADD STATUS TO EACH LECTURE
    # =====================================================

    for lecture in selected_lectures:

        lecture.today_status = selected_attendance.get(
            lecture.id
        )

    # =====================================================
    # ATTENDANCE RECORDS
    # =====================================================

    records = Attendance.objects.filter(
        timetable__compulsory=True
    ).exclude(
        status="NOT_HELD"
    )

    # =====================================================
    # SEMESTER FILTER
    # =====================================================

    if semester:

        records = records.filter(
            date__gte=semester.start_date
        )

    # =====================================================
    # NEVER COUNT FUTURE RECORDS
    # =====================================================

    records = records.filter(
        date__lte=today
    )

    # =====================================================
    # OVERALL ATTENDANCE
    # =====================================================

    conducted = records.count()

    present = records.filter(
        status="PRESENT"
    ).count()

    bunked = records.filter(
        status="BUNK"
    ).count()

    if conducted > 0:

        percentage = (
            present / conducted
        ) * 100

    else:

        percentage = 0

    # =====================================================
    # POSSIBLE BUNKS
    # =====================================================

    possible_bunks = 0

    if conducted > 0 and percentage >= 75:

        possible_bunks = int(
            (present / 0.75) - conducted
        )

        possible_bunks = max(
            possible_bunks,
            0
        )

    # =====================================================
    # LECTURES NEEDED TO REACH 75%
    # =====================================================

    lectures_needed = 0

    if conducted > 0 and percentage < 75:

        lectures_needed = ceil(
            (0.75 * conducted - present) / 0.25
        )

    # =====================================================
    # SUBJECT-WISE ATTENDANCE
    # =====================================================

    subject_data = []

    subject_ids = records.values_list(
        "timetable__subject_id",
        flat=True
    ).distinct()

    for subject_id in subject_ids:

        subject_records = records.filter(
            timetable__subject_id=subject_id
        )

        first_record = subject_records.select_related(
            "timetable__subject"
        ).first()

        if first_record is None:
            continue

        subject_conducted = subject_records.count()

        subject_present = subject_records.filter(
            status="PRESENT"
        ).count()

        subject_bunked = subject_records.filter(
            status="BUNK"
        ).count()

        if subject_conducted > 0:

            subject_percentage = (
                subject_present /
                subject_conducted
            ) * 100

        else:

            subject_percentage = 0

        subject_data.append({

            "subject":
                first_record.timetable.subject,

            "present":
                subject_present,

            "bunked":
                subject_bunked,

            "conducted":
                subject_conducted,

            "percentage":
                round(
                    subject_percentage,
                    2
                ),
        })

    # =====================================================
    # SORT SUBJECTS
    # =====================================================

    subject_data.sort(
        key=lambda item: item["subject"].name
    )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "today":
            today,

        "today_name":
            selected_day_name,

        "selected_date":
            selected_date,

        "selected_date_value":
            selected_date.strftime(
                "%Y-%m-%d"
            ),

        "semester":
            semester,

        "semester_start":
            semester.start_date
            if semester else None,

        "todays_lectures":
            selected_lectures,

        "today_attendance":
            selected_attendance,

        "present":
            present,

        "bunked":
            bunked,

        "conducted":
            conducted,

        "percentage":
            round(
                percentage,
                2
            ),

        "possible_bunks":
            possible_bunks,

        "lectures_needed":
            lectures_needed,

        "subject_data":
            subject_data,
    }

    return render(
        request,
        "attendance/dashboard.html",
        context
    )


# =========================================================
# MARK ATTENDANCE
# =========================================================

@require_POST
def mark_attendance(
    request,
    timetable_id
):

    # =====================================================
    # GET TIMETABLE
    # =====================================================

    timetable = get_object_or_404(
        Timetable,
        id=timetable_id
    )

    # =====================================================
    # GET STATUS
    # =====================================================

    status = request.POST.get(
        "status"
    )

    # =====================================================
    # VALIDATE STATUS
    # =====================================================

    if status not in [
        "PRESENT",
        "BUNK",
        "NOT_HELD"
    ]:

        return redirect(
            "dashboard"
        )

    # =====================================================
    # GET SELECTED DATE
    # =====================================================

    selected_date_text = request.POST.get(
        "attendance_date"
    )

    today = timezone.localdate()

    try:

        attendance_date = datetime.strptime(
            selected_date_text,
            "%Y-%m-%d"
        ).date()

    except (
        ValueError,
        TypeError
    ):

        attendance_date = today

    # =====================================================
    # NEVER ALLOW FUTURE ATTENDANCE
    # =====================================================

    if attendance_date > today:

        attendance_date = today

    # =====================================================
    # SAVE / UPDATE ATTENDANCE
    # =====================================================

    Attendance.objects.update_or_create(

        date=attendance_date,

        timetable=timetable,

        defaults={
            "status": status
        }
    )

    # =====================================================
    # RETURN TO THE SAME LECTURE
    # =====================================================

    return redirect(
        f"/?date={attendance_date.strftime('%Y-%m-%d')}"
        f"#lecture-{timetable.id}"
    )