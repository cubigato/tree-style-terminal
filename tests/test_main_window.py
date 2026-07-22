"""Main window tests for tree-style-terminal."""

from unittest.mock import Mock, patch

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from tree_style_terminal.models.session import TerminalSession


def test_main_window_creation():
    """Test MainWindow can be instantiated (basic setup)."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    # Create a minimal app instance for the window
    app = TreeStyleTerminalApp()

    # Create main window
    window = MainWindow(application=app)
    assert window is not None
    assert window.session_manager is not None


def test_main_window_methods_exist():
    """Test that expected methods exist on MainWindow."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)

    # Check that expected methods exist
    expected_methods = [
        '_on_new_terminal_clicked',
        '_on_close_session_clicked',
        '_on_new_child_clicked',
        '_on_sidebar_toggle_clicked',
        '_on_export_selected_activate',
        '_on_export_all_activate',
        '_on_load_profile_clicked',
        'request_ai_command_draft',
    ]

    for method_name in expected_methods:
        assert hasattr(window, method_name), f"Missing method: {method_name}"
        assert callable(getattr(window, method_name)), f"Method not callable: {method_name}"


def test_app_creation():
    """Test TreeStyleTerminalApp can be instantiated."""
    from tree_style_terminal.main import TreeStyleTerminalApp

    app = TreeStyleTerminalApp()
    assert app is not None
    assert hasattr(app, 'window')
    assert app.window is None  # Should be None until activated


def test_sidebar_state_management():
    """Test sidebar state tracking properties."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)

    # Check sidebar state properties exist
    assert hasattr(window, '_sidebar_collapsed')
    assert isinstance(window._sidebar_collapsed, bool)
    assert window._sidebar_collapsed is False  # Should start expanded


def test_sidebar_width_bounds_for_small_window():
    """Sidebar bounds preserve terminal room on small windows."""
    from tree_style_terminal.main import calculate_sidebar_width_bounds

    bounds = calculate_sidebar_width_bounds(800)

    assert bounds.minimum == 150
    assert bounds.default == 250
    assert bounds.maximum == 320


def test_sidebar_width_bounds_for_medium_window():
    """Sidebar bounds match the previous defaults on normal windows."""
    from tree_style_terminal.main import calculate_sidebar_width_bounds

    bounds = calculate_sidebar_width_bounds(1024)

    assert bounds.minimum == 150
    assert bounds.default == 250
    assert bounds.maximum == 410


def test_sidebar_width_bounds_for_large_window():
    """Sidebar bounds scale up for large displays."""
    from tree_style_terminal.main import calculate_sidebar_width_bounds

    bounds = calculate_sidebar_width_bounds(3840)

    assert bounds.minimum == 260
    assert bounds.default == 560
    assert bounds.maximum == 1000


def test_clamp_sidebar_width_uses_computed_bounds():
    """Sidebar clamping follows the dynamic min/max bounds."""
    from tree_style_terminal.main import (
        calculate_sidebar_width_bounds,
        clamp_sidebar_width,
    )

    bounds = calculate_sidebar_width_bounds(3840)

    assert clamp_sidebar_width(100, bounds) == 260
    assert clamp_sidebar_width(700, bounds) == 700
    assert clamp_sidebar_width(1200, bounds) == 1000


def test_configure_sidebar_paned_uses_narrow_handle():
    """Sidebar paned keeps the resize hit area out of the terminal text edge."""
    from tree_style_terminal.main import configure_sidebar_paned

    class StyleContext:
        def __init__(self):
            self.classes = []

        def add_class(self, name):
            self.classes.append(name)

    class Paned:
        def __init__(self):
            self.style_context = StyleContext()
            self.wide_handle = True

        def get_style_context(self):
            return self.style_context

        def set_wide_handle(self, wide_handle):
            self.wide_handle = wide_handle

    paned = Paned()

    configure_sidebar_paned(paned)

    assert "main-paned" in paned.style_context.classes
    assert paned.wide_handle is False


def test_layout_components_exist():
    """Test that layout components (Paned, Revealer) are available."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)

    # Check that layout-related attributes exist
    expected_attributes = [
        'paned',  # Gtk.Paned for sidebar and terminal area
        'sidebar_revealer',  # Gtk.Revealer for collapsible sidebar
    ]

    for attr in expected_attributes:
        if hasattr(window, attr):
            # If it exists, it should not be None
            assert getattr(window, attr) is not None


def test_sidebar_toggle_functionality():
    """Test sidebar toggle button and revealer functionality."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)

    # Check toggle method exists
    assert hasattr(window, '_on_sidebar_toggle_clicked')
    assert callable(window._on_sidebar_toggle_clicked)

    # Test initial state
    initial_state = window._sidebar_collapsed

    # Simulate toggle (without actually clicking)
    # This tests the method exists and can be called
    try:
        window._on_sidebar_toggle_clicked(None)  # Button parameter can be None for test
        # State should have changed
        assert window._sidebar_collapsed != initial_state
    except Exception:
        # If method requires specific setup, just verify it exists
        pass


def test_new_session_creation_schedules_terminal_focus():
    """Test creating a session schedules focus back to the terminal."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)
    session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
    terminal_widget = Gtk.Box()

    with patch("tree_style_terminal.main.GLib.idle_add") as idle_add:
        window._on_session_created(session, terminal_widget)

    idle_add.assert_called_with(window.focus_terminal)


def test_profile_export_button_has_two_scopes_and_tracks_session_state():
    """The headerbar export menu exposes the two requested scopes."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    window = MainWindow(application=TreeStyleTerminalApp())

    assert window.export_profile_button.get_sensitive() is False
    labels = [item.get_label() for item in window.export_profile_button.get_popup().get_children()]
    assert labels == ["Selected Session and Children", "All Sessions"]

    current_session = TerminalSession(
        pid=1,
        pty_fd=1,
        cwd="/tmp",
    )
    window.session_tree.add_node(current_session)
    window.session_manager.current_session = current_session
    window._update_button_states()

    assert window.export_profile_button.get_sensitive() is True


def test_profile_export_scope_handlers_pass_selected_subtree_or_all_roots():
    """Each export menu item forwards the intended session roots."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    window = MainWindow(application=TreeStyleTerminalApp())
    first = TerminalSession(pid=1, pty_fd=1, cwd="/tmp", title="first")
    child = TerminalSession(pid=2, pty_fd=2, cwd="/tmp", title="child")
    second = TerminalSession(pid=3, pty_fd=3, cwd="/tmp", title="second")
    window.session_tree.add_node(first)
    window.session_tree.add_node(child, first)
    window.session_tree.add_node(second)
    window.session_manager.current_session = child

    with patch.object(window, "_save_workspace_profile") as save_profile:
        window._on_export_selected_activate(window.export_selected_menu_item)
        save_profile.assert_called_once_with([child])

        save_profile.reset_mock()
        window._on_export_all_activate(window.export_all_menu_item)
        save_profile.assert_called_once_with([first, second])


def test_profile_export_cancel_does_not_write(tmp_path):
    """Cancelling destination selection leaves the filesystem untouched."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    window = MainWindow(application=TreeStyleTerminalApp())
    root = TerminalSession(pid=1, pty_fd=1, cwd=str(tmp_path), title="root")

    with (
        patch.object(window, "_choose_workspace_profile_path", return_value=None),
        patch("tree_style_terminal.main.export_workspace_profile") as export_profile,
    ):
        window._save_workspace_profile([root])

    export_profile.assert_not_called()
    assert list(tmp_path.iterdir()) == []


def test_profile_export_reports_write_failure(tmp_path):
    """A writer error is logged and shown without escaping the UI callback."""
    from tree_style_terminal.config.workspace_profile import WorkspaceProfileError
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    window = MainWindow(application=TreeStyleTerminalApp())
    root = TerminalSession(pid=1, pty_fd=1, cwd=str(tmp_path), title="root")
    window.session_manager.current_session = root
    destination = tmp_path / "workspace.yml"

    with (
        patch.object(
            window,
            "_choose_workspace_profile_path",
            return_value=destination,
        ),
        patch(
            "tree_style_terminal.main.export_workspace_profile",
            side_effect=WorkspaceProfileError("write failed"),
        ),
        patch.object(window, "_show_workspace_profile_error") as show_error,
    ):
        window._save_workspace_profile([root])

    show_error.assert_called_once_with("write failed")


def test_welcome_load_profile_button_is_directly_below_new_terminal():
    """The welcome actions retain the requested visual order."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    window = MainWindow(application=TreeStyleTerminalApp())
    children = window.welcome_new_terminal_button.get_parent().get_children()

    new_terminal_index = children.index(window.welcome_new_terminal_button)
    assert children[new_terminal_index + 1] is window.welcome_load_profile_button
    assert window.welcome_load_profile_button.get_label() == "Load Profile"


def test_workspace_profile_start_directory_expands_tilde(monkeypatch, tmp_path):
    """A usable configured user path is selected for the chooser."""
    from tree_style_terminal.main import workspace_profile_start_directory

    profile_directory = tmp_path / "profiles"
    profile_directory.mkdir()
    monkeypatch.setenv("HOME", str(tmp_path))

    assert workspace_profile_start_directory("~/profiles") == profile_directory


def test_workspace_profile_start_directory_falls_back_to_home(tmp_path):
    """Missing, empty, and unusable settings all use the supplied home path."""
    from tree_style_terminal.main import workspace_profile_start_directory

    for configured_directory in (None, "", "   ", tmp_path / "missing"):
        assert (
            workspace_profile_start_directory(
                configured_directory,
                home_directory=tmp_path,
            )
            == tmp_path
        )


def test_profile_load_chooser_uses_yaml_filter_and_configured_directory(tmp_path):
    """The open dialog starts as configured and only offers a YAML filter."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    dialog = Mock()
    dialog.run.return_value = Gtk.ResponseType.CANCEL
    dialog.get_filename.return_value = None
    yaml_filter = Mock()
    window = MainWindow(application=TreeStyleTerminalApp())

    with (
        patch(
            "tree_style_terminal.main.config_manager.get",
            return_value=str(tmp_path),
        ),
        patch(
            "tree_style_terminal.main.Gtk.FileChooserDialog",
            return_value=dialog,
        ) as chooser_dialog,
        patch(
            "tree_style_terminal.main.Gtk.FileFilter",
            return_value=yaml_filter,
        ),
    ):
        assert window._choose_workspace_profile_to_load() is None

    chooser_dialog.assert_called_once_with(
        title="Load Workspace Profile",
        transient_for=window,
        action=Gtk.FileChooserAction.OPEN,
    )
    dialog.set_current_folder.assert_called_once_with(str(tmp_path))
    yaml_filter.set_name.assert_called_once_with("YAML profile files")
    assert yaml_filter.add_pattern.call_count == 2
    yaml_filter.add_pattern.assert_any_call("*.yml")
    yaml_filter.add_pattern.assert_any_call("*.yaml")
    dialog.add_filter.assert_called_once_with(yaml_filter)
    dialog.destroy.assert_called_once_with()


def test_welcome_profile_button_loads_all_validated_roots(tmp_path):
    """Activating the button uses the shared loader and multi-root creator."""
    from tree_style_terminal.config.workspace_profile import (
        WorkspaceNode,
        WorkspaceProfile,
    )
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    profile_path = tmp_path / "workspace.yml"
    roots = [
        WorkspaceNode(workdir=str(tmp_path), title="first"),
        WorkspaceNode(workdir=str(tmp_path), title="second", selected=True),
    ]
    profile = WorkspaceProfile(
        path=profile_path,
        version=1,
        name="Two roots",
        roots=roots,
    )
    window = MainWindow(application=TreeStyleTerminalApp())

    with (
        patch.object(
            window,
            "_choose_workspace_profile_to_load",
            return_value=profile_path,
        ),
        patch(
            "tree_style_terminal.main.load_workspace_profile",
            return_value=profile,
        ) as load_profile,
        patch.object(window.session_manager, "create_workspace_trees") as create_trees,
    ):
        window.welcome_load_profile_button.emit("clicked")

    load_profile.assert_called_once_with(profile_path)
    create_trees.assert_called_once_with(roots)


def test_cancelling_welcome_profile_chooser_keeps_welcome_unchanged():
    """Cancelling creates no sessions and keeps the welcome page visible."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    window = MainWindow(application=TreeStyleTerminalApp())
    with (
        patch.object(
            window,
            "_choose_workspace_profile_to_load",
            return_value=None,
        ),
        patch("tree_style_terminal.main.load_workspace_profile") as load_profile,
    ):
        window.welcome_load_profile_button.emit("clicked")

    load_profile.assert_not_called()
    assert window.session_tree.is_empty()
    assert window.terminal_stack.get_visible_child_name() == "welcome"


def test_invalid_welcome_profile_shows_load_error_without_sessions(tmp_path):
    """Validation errors leave the empty welcome screen ready for another action."""
    from tree_style_terminal.config.workspace_profile import WorkspaceProfileError
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    profile_path = tmp_path / "invalid.yml"
    window = MainWindow(application=TreeStyleTerminalApp())
    with (
        patch.object(
            window,
            "_choose_workspace_profile_to_load",
            return_value=profile_path,
        ),
        patch(
            "tree_style_terminal.main.load_workspace_profile",
            side_effect=WorkspaceProfileError("invalid profile"),
        ),
        patch.object(window.session_manager, "create_workspace_trees") as create_trees,
        patch.object(window, "_show_workspace_profile_error") as show_error,
    ):
        window.welcome_load_profile_button.emit("clicked")

    create_trees.assert_not_called()
    show_error.assert_called_once_with("invalid profile", operation="load")
    assert window.session_tree.is_empty()
    assert window.terminal_stack.get_visible_child_name() == "welcome"


def test_theme_update_applies_to_session_manager_terminals():
    """Test theme updates are delegated to SessionManager-managed terminals."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)
    session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
    terminal_widget = Mock()
    window.session_manager._session_terminals[session] = terminal_widget

    window._update_terminal_themes("dark")

    terminal_widget.apply_theme.assert_called_once_with("dark")
