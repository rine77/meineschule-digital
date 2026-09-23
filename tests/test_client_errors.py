from datetime import date

import pytest
from yarl import URL

from meineschule_digital import AuthenticationError, MeineSchuleClient


class FakeResponse:
    def __init__(
        self,
        html="",
        *,
        url="https://meineschule.digital/salza-gymnasium/schedule",
        content_type="text/html",
    ):
        self.html = html
        self.url = URL(url)
        self.content_type = content_type

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self):
        pass

    async def text(self):
        return self.html


class FakeSession:
    def __init__(self, get_responses, post_responses=()):
        self.get_responses = iter(get_responses)
        self.post_responses = iter(post_responses)

    def get(self, *args, **kwargs):
        return next(self.get_responses)

    def post(self, *args, **kwargs):
        return next(self.post_responses)


@pytest.mark.asyncio
async def test_invalid_login_raises_authentication_error():
    login_page = """
    <form>
      <input name="Password" type="password">
      <input name="__RequestVerificationToken" value="synthetic-token">
    </form>
    """
    session = FakeSession(
        get_responses=[FakeResponse(login_page)],
        post_responses=[FakeResponse(login_page)],
    )

    with pytest.raises(AuthenticationError, match="Login fehlgeschlagen"):
        await MeineSchuleClient(session).login("example", "wrong-password")


SCHEDULE_PAGE = """
<select id="Selection">
  <option selected value="s:00000000-0000-0000-0000-000000000001">
    Beispiel
  </option>
</select>
"""


@pytest.mark.asyncio
async def test_schedule_access_denied_has_clear_error():
    session = FakeSession(
        get_responses=[
            FakeResponse(SCHEDULE_PAGE),
            FakeResponse(
                "<h1>Access denied</h1>",
                url="https://meineschule.digital/Account/AccessDenied",
            ),
        ]
    )

    with pytest.raises(PermissionError, match="2026-09-14"):
        await MeineSchuleClient(session).get_schedule(
            "salza-gymnasium", date(2026, 9, 14)
        )


@pytest.mark.asyncio
async def test_schedule_rejects_unexpected_html_response():
    session = FakeSession(
        get_responses=[
            FakeResponse(SCHEDULE_PAGE),
            FakeResponse("<html>Unerwartete Antwort</html>"),
        ]
    )

    with pytest.raises(ValueError, match="Unerwartetes Antwortformat"):
        await MeineSchuleClient(session).get_schedule(
            "salza-gymnasium", date(2026, 9, 16)
        )
