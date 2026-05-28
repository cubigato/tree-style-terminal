import logging
from unittest.mock import MagicMock, patch

from tree_style_terminal.main import configure_logging


def test_configure_logging_uses_cli_level():
    """CLI log level is applied directly."""
    with patch("tree_style_terminal.main.logging.basicConfig") as mock_basic_config:
        configure_logging("error")

    mock_basic_config.assert_called_once_with(
        level=logging.ERROR,
        format="%(levelname)s:%(name)s:%(message)s",
        force=True,
    )


def test_configure_logging_reads_config_when_no_cli_level():
    """Config log level is used when CLI does not override it."""
    mock_config = MagicMock()
    mock_config.get.return_value = "debug"

    with (
        patch("tree_style_terminal.main.config_manager", mock_config),
        patch("tree_style_terminal.main.logging.basicConfig") as mock_basic_config,
    ):
        configure_logging()

    mock_config.load_config.assert_called_once()
    mock_config.get.assert_called_once_with("app.log_level", "warning")
    mock_basic_config.assert_called_once_with(
        level=logging.DEBUG,
        format="%(levelname)s:%(name)s:%(message)s",
        force=True,
    )
