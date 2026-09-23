from datetime import date
from typing import Any

from meineschule_digital.models import ScheduleLesson


def parse_schedule(
    data: dict[str, Any],
    *,
    excluded_subjects: set[str] | None = None,
) -> list[ScheduleLesson]:
    """Liest die tatsächlich angezeigten Stunden einer Plan-Response."""
    excluded = {subject.casefold() for subject in (excluded_subjects or set())}
    lessons: list[ScheduleLesson] = []

    for day in data["schedule"]["days"]:
        lesson_date = date.fromisoformat(day["d"][:10])

        for period, slot in enumerate(day["l"]):
            for entry in slot.get("e", []):
                subject = entry.get("st")
                if not subject or subject.casefold() in excluded:
                    continue

                lessons.append(
                    ScheduleLesson(
                        date=lesson_date,
                        period=period,
                        subject=subject,
                        cancelled=bool(entry.get("cancelled", False)),
                    )
                )

    return lessons
