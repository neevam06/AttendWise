from django.db import models


# =========================================================
# SEMESTER
# =========================================================

class Semester(models.Model):

    name = models.CharField(
        max_length=100,
        default="Current Semester"
    )

    start_date = models.DateField()

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name


# =========================================================
# SUBJECT
# =========================================================

class Subject(models.Model):

    name = models.CharField(
        max_length=100
    )

    code = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return self.name


# =========================================================
# TIMETABLE
# =========================================================

class Timetable(models.Model):

    DAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]

    day = models.CharField(
        max_length=10,
        choices=DAYS
    )

    lecture_number = models.PositiveIntegerField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    teacher = models.CharField(
        max_length=100,
        blank=True
    )

    compulsory = models.BooleanField(
        default=True
    )

    def __str__(self):
        return (
            f"{self.day} - "
            f"Lecture {self.lecture_number} - "
            f"{self.subject.name}"
        )


# =========================================================
# ATTENDANCE
# =========================================================

class Attendance(models.Model):

    STATUS = [
        ('PRESENT', 'Present'),
        ('BUNK', 'Bunk'),
        ('NOT_HELD', 'Not Held'),
    ]

    date = models.DateField()

    timetable = models.ForeignKey(
        Timetable,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'timetable'],
                name='unique_attendance_per_lecture'
            )
        ]

    def __str__(self):
        return (
            f"{self.date} - "
            f"{self.timetable.subject.name} - "
            f"{self.status}"
        )