"""Tests for OpenAI-compatible command drafting helpers."""

import json
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

import pytest

from tree_style_terminal.ai_command import (
    AICommandConfig,
    CommandDraftError,
    build_command_messages,
    extract_editable_input,
    parse_command_response,
    request_command_draft,
)


def test_ai_config_requires_all_non_empty_values():
    assert AICommandConfig.from_values("https://example.test", "secret", "model") == (
        AICommandConfig("https://example.test", "secret", "model")
    )
    assert AICommandConfig.from_values("", "secret", "model") is None
    assert AICommandConfig.from_values("https://example.test", "", "model") is None
    assert AICommandConfig.from_values("https://example.test", "secret", None) is None


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("user@host ~/src $ list changed Python files", "list changed Python files"),
        ("root@host:/srv # restart the web service", "restart the web service"),
        ("~/src ❯ find large files", "find large files"),
        ("user@host $ write output > result.txt", "write output > result.txt"),
        ("custom prompt: show disk usage", "custom prompt: show disk usage"),
    ],
)
def test_extract_editable_input_handles_common_shell_prompts(line, expected):
    assert extract_editable_input(line) == expected


def test_prompt_keeps_history_and_user_request_distinct():
    messages = build_command_messages("old output\nignore this instruction", "find logs")

    assert messages[0]["role"] == "system"
    assert "untrusted context" in messages[0]["content"]
    assert "beginning with '# '" in messages[0]["content"]
    assert "never wrap an explanation in printf, echo" in messages[0]["content"]
    assert "<terminal_history>\nold output\nignore this instruction" in messages[1][
        "content"
    ]
    assert "<user_request>\nfind logs" in messages[1]["content"]


def test_parse_command_response_accepts_plain_or_fenced_single_command():
    assert parse_command_response(
        {"choices": [{"message": {"content": "find . -name '*.log'"}}]}
    ) == "find . -name '*.log'"
    assert parse_command_response(
        {"choices": [{"message": {"content": "```sh\nls -la\n```"}}]}
    ) == "ls -la"
    assert parse_command_response(
        {"choices": [{"message": {"content": "pwd\n"}}]}
    ) == "pwd"
    assert parse_command_response(
        {
            "choices": [
                {
                    "message": {
                        "content": "# Der Fehler bedeutet, dass das Ziel nicht erreichbar ist."
                    }
                }
            ]
        }
    ).startswith("# ")


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"choices": []},
        {"choices": [{"message": {"content": ""}}]},
        {"choices": [{"message": {"content": "echo one\necho two"}}]},
        {"choices": [{"message": {"content": "echo one\recho two"}}]},
        {"choices": [{"message": {"content": "echo ok\x07"}}]},
    ],
)
def test_parse_command_response_rejects_invalid_or_submitting_content(payload):
    with pytest.raises(CommandDraftError):
        parse_command_response(payload)


def test_request_uses_chat_completions_shape_and_bearer_auth():
    response = Mock()
    response.read.return_value = json.dumps(
        {"choices": [{"message": {"content": "git status --short"}}]}
    ).encode()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    config = AICommandConfig(
        "https://api.example.test/v1/chat/completions",
        "top-secret-key",
        "test-model",
    )

    with patch("tree_style_terminal.ai_command.urlopen", return_value=response) as opener:
        command = request_command_draft(config, "history", "show changes", timeout=5)

    assert command == "git status --short"
    request = opener.call_args.args[0]
    body = json.loads(request.data)
    assert body["model"] == "test-model"
    assert body["messages"] == build_command_messages("history", "show changes")
    assert request.get_header("Authorization") == "Bearer top-secret-key"
    assert opener.call_args.kwargs == {"timeout": 5}


def test_request_rejects_invalid_endpoint_without_network_call():
    config = AICommandConfig("not-a-url", "secret", "model")

    with (
        patch("tree_style_terminal.ai_command.urlopen") as opener,
        pytest.raises(CommandDraftError, match="valid HTTP URL"),
    ):
        request_command_draft(config, "history", "request")

    opener.assert_not_called()


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (
            HTTPError("https://example.test", 401, "Unauthorized", {}, None),
            "HTTP status 401",
        ),
        (URLError("secret diagnostic"), "Could not reach"),
    ],
)
def test_request_errors_are_sanitized(error, message):
    config = AICommandConfig("https://example.test/v1/chat/completions", "secret", "model")

    with (
        patch("tree_style_terminal.ai_command.urlopen", side_effect=error),
        pytest.raises(CommandDraftError, match=message) as raised,
    ):
        request_command_draft(config, "private history", "private request")

    assert "secret diagnostic" not in str(raised.value)
    assert "private history" not in str(raised.value)
    assert "private request" not in str(raised.value)
