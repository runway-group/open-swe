"""RG-640 regression coverage for the managed LangSmith endpoint override."""

from unittest.mock import patch

from agent.sandboxes.providers.langsmith import _get_sandbox_api_endpoint


def test_open_swe_langsmith_endpoint_override_takes_precedence() -> None:
    with patch.dict(
        "os.environ",
        {
            "LANGSMITH_ENDPOINT": "https://api.smith.langchain.com",
            "OPEN_SWE_LANGSMITH_ENDPOINT": "https://apac.api.smith.langchain.com",
        },
        clear=True,
    ):
        assert (
            _get_sandbox_api_endpoint()
            == "https://apac.api.smith.langchain.com/v2/sandboxes"
        )


def test_langsmith_endpoint_is_used_when_override_is_unset() -> None:
    with patch.dict(
        "os.environ",
        {"LANGSMITH_ENDPOINT": "https://eu.smith.langchain.com"},
        clear=True,
    ):
        assert _get_sandbox_api_endpoint() == "https://eu.smith.langchain.com/v2/sandboxes"
