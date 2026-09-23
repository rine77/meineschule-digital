import pytest

from meineschule_digital.auth import (
    AuthenticationError,
    get_verification_token,
    require_authenticated_page,
)


def test_login_form_requires_csrf_token():
    with pytest.raises(AuthenticationError, match="CSRF-Token"):
        get_verification_token("<form><input name='UserName'></form>")


def test_expired_session_is_recognized_by_password_field():
    html = """
    <form action="/account/login">
      <input name="UserName">
      <input name="Password" type="password">
    </form>
    """
    with pytest.raises(AuthenticationError, match="Session abgelaufen"):
        require_authenticated_page(html)


def test_authenticated_page_without_login_form_is_accepted():
    require_authenticated_page(
        '<main><h3>Noten</h3><p>Keine Einträge</p></main>'
    )
