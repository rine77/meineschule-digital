from datetime import date, timedelta
from collections.abc import Collection, Iterable

from meineschule_digital.models import Lesson, ScheduleLesson


def _week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def _weeks_between(start: date, end: date):
    current = _week_start(start)
    last = _week_start(end)

    while current <= last:
        yield current
        current += timedelta(days=7)


def resolve_due_date(
    homework: Lesson,
    schedule_lessons: Iterable[ScheduleLesson],
    covered_weeks: Collection[date],
) -> date | None:
    """Ermittelt das ausdrückliche oder das nächste belegte Fachdatum.

    covered_weeks enthält die Montage aller erfolgreich abgefragten Planwochen.
    Ohne lückenlose Abdeckung ab dem Aufgabedatum wird nichts geschätzt.
    """
    if homework.due_date is not None:
        return homework.due_date

    candidates = sorted(
        {
            item.date
            for item in schedule_lessons
            if item.date > homework.date
            and item.subject.casefold() == homework.subject.casefold()
            and not item.cancelled
        }
    )

    for candidate in candidates:
        if all(week in covered_weeks for week in _weeks_between(homework.date, candidate)):
            return candidate

    return None
