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
class Lesson:
    date: date
    subject: str
    homework: str


@dataclass
class HomeInfo:
    student: str
    grades: list[Grade] = field(default_factory=list)
    lessons: list[Lesson] = field(default_factory=list)
