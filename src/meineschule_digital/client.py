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
