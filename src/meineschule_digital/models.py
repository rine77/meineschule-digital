from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Grade:
    subject: str
    date: date
    value: str
    remark: str
    information: str


@dataclass(frozen=True)
class Absence:
    date: date
    remark: str


@dataclass(frozen=True)
class StudentRemark:
    date: date
    text: str
    subject: str
    type: str
    author: str


@dataclass(frozen=True)
class Lesson:
    date: date
    subject: str
    homework: str
    due_date: date | None = None  # Nur ausdrücklich genanntes "zum DD.MM.JJJJ"

@dataclass
class HomeInfo:
    student: str
    grades: list[Grade] = field(default_factory=list)
    absences: list[Absence] = field(default_factory=list)
    remarks: list[StudentRemark] = field(default_factory=list)
    lessons: list[Lesson] = field(default_factory=list)


@dataclass(frozen=True)
class ScheduleLesson:
    date: date
    period: int
    subject: str
    cancelled: bool
