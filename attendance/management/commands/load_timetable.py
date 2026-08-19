from django.core.management.base import BaseCommand
from attendance.models import Subject, Timetable
from datetime import time


class Command(BaseCommand):
    help = "Load 3K3 timetable"

    def handle(self, *args, **kwargs):

        timetable_data = [

            # =========================
            # MONDAY
            # =========================
            ("Monday", 1, "09:00", "09:55", "DBMS", "PKM", True),
            ("Monday", 2, "09:55", "10:50", "DSA", "SVP", True),
            ("Monday", 3, "11:00", "11:55", "DMSM", "UP", True),
            ("Monday", 4, "11:55", "12:50", "OOPJ", "NT", True),
            ("Monday", 5, "13:20", "14:15", "DBMS", "PKM", True),
            ("Monday", 6, "14:15", "15:10", "DBMS", "PKM", True),

            # =========================
            # TUESDAY
            # =========================
            ("Tuesday", 1, "09:00", "09:55", "DAT", "RKP", True),
            ("Tuesday", 2, "09:55", "10:50", "DAT", "RKP", True),
            ("Tuesday", 3, "11:00", "11:55", "DAT", "PKM", True),
            ("Tuesday", 4, "11:55", "12:50", "DAT", "PKM", True),
            ("Tuesday", 5, "13:20", "14:15", "DMSM", "KP", True),
            ("Tuesday", 6, "14:15", "15:10", "DBMS", "SAP", True),

            # =========================
            # WEDNESDAY
            # =========================
            ("Wednesday", 1, "09:00", "09:55", "DSA", "SVP", True),
            ("Wednesday", 2, "09:55", "10:50", "DSA", "SVP", True),
            ("Wednesday", 3, "11:00", "11:55", "OOPJ", "RKP", True),
            ("Wednesday", 4, "11:55", "12:50", "DSA", "SVP", True),
            ("Wednesday", 5, "13:20", "14:15", "DMSM", "KP", True),
            ("Wednesday", 6, "14:15", "15:10", "DBMS", "SAP", True),

            # =========================
            # THURSDAY
            # =========================
            ("Thursday", 1, "09:00", "09:55", "DSA", "PC", True),
            ("Thursday", 2, "09:55", "10:50", "DSA", "PC", True),
            ("Thursday", 3, "11:00", "11:55", "DMSM", "UP", True),
            ("Thursday", 4, "11:55", "12:50", "DSA", "PC", True),
            ("Thursday", 5, "13:20", "14:15", "OOPJ", "RKP", True),
            ("Thursday", 6, "14:15", "15:10", "OOPJ", "RKP", True),

            # =========================
            # FRIDAY
            # =========================
            ("Friday", 1, "09:00", "09:55", "DMSM", "KAS", True),
            ("Friday", 2, "09:55", "10:50", "DMSM", "KAS", True),
            ("Friday", 3, "11:00", "11:55", "OOPJ", "NT", True),
            ("Friday", 4, "11:55", "12:50", "OOPJ", "NT", True),
            ("Friday", 5, "13:20", "14:15", "DMSM", "KP", True),
            ("Friday", 6, "14:15", "15:10", "IKS", "MK", True),

            # =========================
            # SATURDAY - OPTIONAL
            # =========================
            ("Saturday", 1, "09:00", "09:55", "DBMS", "PKM", False),
            ("Saturday", 2, "09:55", "10:50", "OOPJ", "RKP", False),
            ("Saturday", 3, "11:00", "11:55", "CSL", "NT", False),

        ]

        created_count = 0

        for day, lecture, start, end, subject_name, teacher, compulsory in timetable_data:

            subject = Subject.objects.get(name=subject_name)

            start_hour, start_minute = map(int, start.split(":"))
            end_hour, end_minute = map(int, end.split(":"))

            _, created = Timetable.objects.update_or_create(
                day=day,
                lecture_number=lecture,
                defaults={
                    "start_time": time(start_hour, start_minute),
                    "end_time": time(end_hour, end_minute),
                    "subject": subject,
                    "teacher": teacher,
                    "compulsory": compulsory,
                }
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"3K3 timetable loaded successfully! "
                f"{created_count} records created."
            )
        )