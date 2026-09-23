from datetime import date

from meineschule_digital.parsers.schedule import parse_schedule


def test_schedule_skips_excluded_subject_and_preserves_empty_day():
    data = {
        "schedule": {
            "days": [
                {
                    "d": "2026-09-22T00:00:00",
                    "l": [
                        {"s": [], "e": []},
                        {
                            "s": [],
                            "e": [
                                {"st": "ER", "cancelled": False},
                                {"st": "Et", "cancelled": False},
                            ],
                        },
                    ],
                },
                {
                    "d": "2026-09-23T00:00:00",
                    "l": [{"s": [], "e": []}],
                },
                {
                    "d": "2026-09-24T00:00:00",
                    "l": [
                        {"s": [], "e": []},
                        {"s": [], "e": [{"st": "Ma", "cancelled": True}]},
                    ],
                },
            ]
        }
    }

    lessons = parse_schedule(data, excluded_subjects={"er"})

    assert len(lessons) == 2
    assert lessons[0].date == date(2026, 9, 22)
    assert lessons[0].period == 1
    assert lessons[0].subject == "Et"
    assert lessons[1].date == date(2026, 9, 24)
    assert lessons[1].cancelled is True
    assert all(lesson.date != date(2026, 9, 23) for lesson in lessons)
