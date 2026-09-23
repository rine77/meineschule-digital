from bs4 import BeautifulSoup


class AuthenticationError(Exception):
    """Login failed or the expected login form was not found."""


def get_verification_token(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    field = soup.select_one('input[name="__RequestVerificationToken"]')

    if field is None or not field.get("value"):
        raise AuthenticationError("CSRF-Token auf der Loginseite nicht gefunden")

    return str(field["value"])
