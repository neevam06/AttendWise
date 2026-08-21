from datetime import datetime

import pandas as pd

from django.core.management.base import BaseCommand

from attendance.models import Timetable, Attendance


class Command(BaseCommand):

    help = "Import attendance history from AttendWise.xlsx"

    def add_arguments(self, parser):

        parser.add_argument(
            "--file",
            default="AttendWise.xlsx",
            help="Excel file path"
        )

    def handle(self, *args, **options):

        file_path = options["file"]

        self.stdout.write(
            self.style.WARNING(
                f"Reading Excel file: {file_path}"
            )
        )

        # =====================================================
        # READ EXCEL
        # =====================================================

        try:

            df = pd.read_excel(
                file_path,
                header=None
            )

        except Exception as e:

            self.stdout.write(
                self.style.ERROR(
                    f"Could not read Excel file: {e}"
                )
            )

            return

        if df.shape[1] < 2:

            self.stdout.write(
                self.style.ERROR(
                    "Excel must contain at least two columns: Date and Status."
                )
            )

            return

        # =====================================================
        # STATISTICS
        # =====================================================

        created = 0
        updated = 0
        skipped = 0

        # =====================================================
        # PROCESS EACH ROW
        # =====================================================

        for _, row in df.iterrows():

            raw_date = row.iloc[0]
            raw_status = row.iloc[1]

            # -------------------------------------------------
            # EMPTY ROW
            # -------------------------------------------------

            if pd.isna(raw_date) or pd.isna(raw_status):

                skipped += 1
                continue

            # -------------------------------------------------
            # DATE
            # -------------------------------------------------

            try:

                attendance_date = pd.to_datetime(
                    raw_date
                ).date()

            except Exception:

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped invalid date: {raw_date}"
                    )
                )

                skipped += 1
                continue

            description = str(
                raw_status
            ).strip().lower()

            # -------------------------------------------------
            # HOLIDAY
            # -------------------------------------------------

            if "holiday" in description:

                self.stdout.write(
                    f"{attendance_date}: Holiday - skipped"
                )

                skipped += 1
                continue

            # -------------------------------------------------
            # OPTIONAL SATURDAY
            # -------------------------------------------------

            if "optional" in description:

                self.stdout.write(
                    f"{attendance_date}: Optional Saturday - skipped"
                )

                skipped += 1
                continue

            # -------------------------------------------------
            # GET TIMETABLE FOR THAT DAY
            # -------------------------------------------------

            day_name = attendance_date.strftime(
                "%A"
            )

            lectures = Timetable.objects.filter(
                day=day_name
            ).order_by(
                "lecture_number"
            )

            if not lectures.exists():

                self.stdout.write(
                    self.style.WARNING(
                        f"{attendance_date}: "
                        f"No timetable found for {day_name}"
                    )
                )

                skipped += 1
                continue

            # -------------------------------------------------
            # DETERMINE LECTURE STATUS
            # -------------------------------------------------

            if "all conducted" in description:

                lecture_statuses = {
                    lecture.lecture_number:
                        "PRESENT"

                    for lecture in lectures
                }

            elif (
                "start-4" in description
                and "last 2" in description
            ):

                lecture_statuses = {}

                for lecture in lectures:

                    if lecture.lecture_number <= 4:

                        lecture_statuses[
                            lecture.lecture_number
                        ] = "PRESENT"

                    else:

                        lecture_statuses[
                            lecture.lecture_number
                        ] = "BUNK"

            elif "all 6 bunk" in description:

                lecture_statuses = {
                    lecture.lecture_number:
                        "BUNK"

                    for lecture in lectures
                }

            else:

                self.stdout.write(
                    self.style.WARNING(
                        f"{attendance_date}: "
                        f"Unknown status '{raw_status}'"
                    )
                )

                skipped += 1
                continue

            # -------------------------------------------------
            # SAVE ATTENDANCE
            # -------------------------------------------------

            for lecture in lectures:

                status = lecture_statuses.get(
                    lecture.lecture_number
                )

                if not status:
                    continue

                # Optional/non-compulsory lectures are not
                # included in normal attendance calculation.

                if not lecture.compulsory:
                    continue

                attendance, created_flag = (
                    Attendance.objects.update_or_create(

                        date=attendance_date,

                        timetable=lecture,

                        defaults={
                            "status": status
                        }
                    )
                )

                if created_flag:

                    created += 1

                else:

                    updated += 1

                self.stdout.write(
                    f"{attendance_date} | "
                    f"Lecture {lecture.lecture_number} | "
                    f"{lecture.subject.name} | "
                    f"{status}"
                )

        # =====================================================
        # FINAL RESULT
        # =====================================================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "===================================="
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Attendance import completed!"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created: {created}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated: {updated}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Skipped: {skipped}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "===================================="
            )
        )