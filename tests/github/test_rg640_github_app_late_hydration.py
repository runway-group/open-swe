"""RG-640 regression coverage for late GitHub App secret hydration."""

from typing import Any

import pytest

from agent.github import app as github_app


class _Response:
    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict[str, str]:
        return {"token": "late-token", "expires_at": "2099-01-01T00:00:00Z"}


class _Client:
    last_post: dict[str, Any] | None = None

    def __init__(self, **kwargs: Any) -> None:
        pass

    async def __aenter__(self) -> "_Client":
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    async def post(self, url: str, **kwargs: Any) -> _Response:
        type(self).last_post = {"url": url, **kwargs}
        return _Response()


@pytest.mark.asyncio
async def test_installation_token_observes_late_secret_hydration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    github_app.clear_app_token_cache()

    # Simulate managed deployment import occurring before secrets are hydrated.
    monkeypatch.setattr(github_app, "GITHUB_APP_ID", "")
    monkeypatch.setattr(github_app, "GITHUB_APP_PRIVATE_KEY", "")
    monkeypatch.setattr(github_app, "GITHUB_APP_INSTALLATION_ID", "")

    # Secrets become available later via the lazy central ENV registry.
    monkeypatch.setenv("GITHUB_APP_ID", "14927218")
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY", "late-private-key")
    monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "161288985")

    monkeypatch.setattr(github_app, "_generate_app_jwt", lambda: "jwt")
    monkeypatch.setattr(github_app.httpx2, "AsyncClient", _Client)

    token, expires_at = await github_app.get_github_app_installation_token_with_expiry()

    assert token == "late-token"
    assert expires_at == "2099-01-01T00:00:00Z"
    assert _Client.last_post is not None
    assert _Client.last_post["url"].endswith(
        "/app/installations/161288985/access_tokens"
    )
