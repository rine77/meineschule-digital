from datetime import date

from meineschule_digital.homework import resolve_due_date
from meineschule_digital.models import Lesson, ScheduleLesson


def test_explicit_date_has_priority():
    homework = Lesson(
        date=date(2026, 9, 22),
        subject="et",
        homework="Mindmap zum 06.10.2026",
        due_date=date(2026, 10, 6),
    )
    schedule = [
        ScheduleLesson(date(2026, 9, 29), 3, "Et", False),
    ]

    assert resolve_due_date(homework, schedule, set()) == date(2026, 10, 6)


def test_next_lesson_skips_empty_day_and_cancelled_lesson():
    homework = Lesson(date(2026, 9, 22), "en", "Vokabeln üben")
    schedule = [
        ScheduleLesson(date(2026, 9, 24), 3, "En", True),
        ScheduleLesson(date(2026, 9, 25), 5, "Ma", False),
        ScheduleLesson(date(2026, 9, 28), 5, "En", False),
    ]

    assert resolve_due_date(
        homework,
        schedule,
        {date(2026, 9, 21), date(2026, 9, 28)},
    ) == date(2026, 9, 28)


def test_missing_plan_week_does_not_produce_a_guess():
    homework = Lesson(date(2026, 9, 22), "la", "Vokabeln")
    schedule = [
        ScheduleLesson(date(2026, 10, 6), 1, "La", False),
    ]

    assert resolve_due_date(
        homework,
        schedule,
        {date(2026, 9, 21), date(2026, 10, 5)},
    ) is None


def test_homework_item_reports_due_date_source():
    from meineschule_digital.homework import build_homework_item

    explicit = Lesson(
        date(2026, 9, 22), "et", "Mindmap zum 06.10.2026", date(2026, 10, 6)
    )
    inferred = Lesson(date(2026, 9, 22), "en", "Vokabeln")
    schedule = [ScheduleLesson(date(2026, 9, 24), 3, "En", False)]
    weeks = {date(2026, 9, 21)}

    assert build_homework_item(explicit, [], set()).due_date_source == "explicit"

    result = build_homework_item(inferred, schedule, weeks)
    assert result.due_date == date(2026, 9, 24)
    assert result.due_date_source == "schedule"

    assert build_homework_item(inferred, [], weeks).due_date_source == "unknown"
