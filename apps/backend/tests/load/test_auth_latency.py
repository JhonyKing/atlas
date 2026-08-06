from time import perf_counter
from uuid import UUID

from atlas.auth.fake_provider import FakeAuthProvider
from atlas.auth.service import SessionService


def test_authentication_terminal_states_stay_under_three_seconds_locally() -> None:
    service = SessionService(
        FakeAuthProvider(
            {"ana@example.test": ("secret", UUID("00000000-0000-0000-0000-000000000001"))}
        )
    )
    started = perf_counter()

    for _ in range(100):
        issued = service.login("ana@example.test", "secret")
        renewed = service.renew(issued.access_token)
        assert service.logout(renewed.access_token)

    assert perf_counter() - started < 3.0
