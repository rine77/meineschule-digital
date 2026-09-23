"""Unofficial Python client for MeineSchule.digital."""

from meineschule_digital.auth import AuthenticationError
from meineschule_digital.client import MeineSchuleClient
from meineschule_digital.models import (
    Absence,
    Grade,
    HomeInfo,
    HomeworkItem,
    Lesson,
    ScheduleLesson,
    StudentRemark,
)

__all__ = [
    "Absence",
    "AuthenticationError",
    "Grade",
    "HomeInfo",
    "HomeworkItem",
    "Lesson",
    "MeineSchuleClient",
    "ScheduleLesson",
    "StudentRemark",
]
