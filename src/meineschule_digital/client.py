import re

import aiohttp
from bs4 import BeautifulSoup

from meineschule_digital.auth import AuthenticationError, get_verification_token
from meineschule_digital.models import HomeInfo
from meineschule_digital.parsers.hip import parse_hip


BASE_URL = "https://meineschule.digital"


class MeineSchuleClient:
    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    async def login(self, username: str, password: str) -> None:
        async with self._session.get(f"{BASE_URL}/account/login") as response:
            response.raise_for_status()
            login_html = await response.text()

        token = get_verification_token(login_html)

        async with self._session.post(
            f"{BASE_URL}/account/login",
            data={
                "UserName": username,
                "Password": password,
                "RememberMe": "false",
                "__RequestVerificationToken": token,
            },
        ) as response:
            response.raise_for_status()
            html = await response.text()

        soup = BeautifulSoup(html, "html.parser")

        if soup.select_one('input[name="Password"]'):
            raise AuthenticationError("Login fehlgeschlagen; Zugangsdaten prüfen")

        if soup.select_one('form[action="/account/logout"]') is None:
            raise AuthenticationError(
                "Loginstatus unklar; erwarteten Abmelde-Link nicht gefunden"
            )

    async def get_home_info_html(self, path: str) -> str:
        """Ruft einen bereits bekannten HIP-Pfad ab."""
        if not path.startswith("/") or path.startswith("//"):
            raise ValueError("Ein relativer Pfad beginnend mit / ist erforderlich")

        async with self._session.get(f"{BASE_URL}{path}") as response:
            response.raise_for_status()
            html = await response.text()

        if 'name="Password"' in html:
            raise AuthenticationError("Session abgelaufen oder nicht angemeldet")

        return html

    async def get_home_info(self, school_slug: str) -> HomeInfo:
        """Liest Home.InfoPoint für die angegebene Schule."""
        if not re.fullmatch(r"[a-z0-9-]+", school_slug):
            raise ValueError("Ungültiger Schulpfad")

        html = await self.get_home_info_html(f"/{school_slug}/hip")
        return parse_hip(html)

    async def get_schedule(
        self,
        school_slug: str,
        day,
        *,
        excluded_subjects: set[str] | None = None,
    ):
        """Liest die Stundenplan-Woche, in die day fällt."""
        from datetime import date

        from meineschule_digital.parsers.schedule import parse_schedule

        if not re.fullmatch(r"[a-z0-9-]+", school_slug):
            raise ValueError("Ungültiger Schulpfad")
        if not isinstance(day, date):
            raise TypeError("day muss ein datetime.date sein")

        url = f"{BASE_URL}/{school_slug}/schedule"

        async with self._session.get(url) as response:
            response.raise_for_status()
            page_html = await response.text()

        soup = BeautifulSoup(page_html, "html.parser")
        selected = soup.select_one('#Selection option[selected][value^="s:"]')
        if selected is None:
            raise ValueError("Ausgewählten Schüler im Stundenplan nicht gefunden")

        student_id = str(selected["value"]).removeprefix("s:")

        async with self._session.get(
                url,
                params={
                    "handler": "Schedule",
                    "date": day.isoformat(),
                    "cog": "",
                    "t": "",
                    "s": student_id,
                    "view": "",
                },
        ) as response:
            response.raise_for_status()

            if response.url.path.casefold() == "/account/accessdenied":
                raise PermissionError(
                    f"Kein Zugriff auf die Planwoche mit Datum {day.isoformat()}"
                )

            if response.content_type != "application/json":
                raise ValueError(
                    f"Unerwartetes Antwortformat für Planwoche {day.isoformat()}: "
                    f"{response.content_type}"
                )

            data = await response.json()

        return parse_schedule(data, excluded_subjects=excluded_subjects)

    async def get_schedule_weeks(
        self,
        school_slug: str,
        first_day,
        last_day,
        *,
        excluded_subjects: set[str] | None = None,
    ):
        """Lädt alle Planwochen zwischen first_day und last_day einschließlich."""
        from datetime import date, timedelta

        if not isinstance(first_day, date) or not isinstance(last_day, date):
            raise TypeError("first_day und last_day müssen datetime.date sein")
        if last_day < first_day:
            raise ValueError("last_day liegt vor first_day")

        current = first_day - timedelta(days=first_day.weekday())
        final = last_day - timedelta(days=last_day.weekday())
        weeks = (final - current).days // 7 + 1

        if weeks > 12:
            raise ValueError("Höchstens 12 Wochen pro Aufruf")

        lessons = []
        covered_weeks = set()

        while current <= final:
            week_lessons = await self.get_schedule(
                school_slug,
                current + timedelta(days=2),  # Mittwoch derselben Woche
                excluded_subjects=excluded_subjects,
            )
            lessons.extend(week_lessons)
            covered_weeks.add(current)
            current += timedelta(days=7)

        return lessons, covered_weeks

    async def get_homework(
        self,
        school_slug: str,
        from_date,
        until_date,
        *,
        excluded_subjects: set[str] | None = None,
    ):
        """Liest Hausaufgaben ab from_date und löst Termine bis until_date auf."""
        from datetime import date

        from meineschule_digital.homework import build_homework_item

        if not isinstance(from_date, date) or not isinstance(until_date, date):
            raise TypeError("from_date und until_date müssen datetime.date sein")
        if until_date < from_date:
            raise ValueError("until_date liegt vor from_date")

        excluded = {
            subject.casefold() for subject in (excluded_subjects or set())
        }

        info = await self.get_home_info(school_slug)
        homework = [
            item for item in info.lessons
            if item.date >= from_date
            and item.subject.casefold() not in excluded
            and item.homework
        ]

        unresolved = [item for item in homework if item.due_date is None]
        schedule = []
        covered_weeks = set()

        if unresolved:
            schedule, covered_weeks = await self.get_schedule_weeks(
                school_slug,
                min(item.date for item in unresolved),
                until_date,
                excluded_subjects=excluded,
            )

        return [
            build_homework_item(item, schedule, covered_weeks)
            for item in homework
        ]
