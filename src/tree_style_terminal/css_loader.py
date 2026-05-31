"""CSS loading, theme detection, and DPI scaling for Tree Style Terminal."""

import logging
import os
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk, GLib, Gtk

from .config import ConfigError, config_manager

# Keep the logger name stable for this behavior-preserving extraction.
logger = logging.getLogger("tree_style_terminal.main")


class CSSLoader:
    """Handles CSS loading and theme management for the application."""

    def __init__(self, override_dpi=None):
        self.css_provider = Gtk.CssProvider()
        self.theme_provider = Gtk.CssProvider()
        self.system_css_provider = Gtk.CssProvider()

        # Load configuration for theme detection and DPI scaling
        try:
            config_manager.load_config()
            config_theme = config_manager.get("theme", "automatic")
            if config_theme == "automatic":
                self.current_theme = self._detect_system_theme()
            else:
                self.current_theme = config_theme

            # Read DPI scale from config
            self._config_dpi_scale = config_manager.get("display.dpi_scale", "auto")
        except ConfigError as e:
            logger.error("Configuration error: %s", e)
            raise

        self._override_dpi = override_dpi

    def load_base_css(self):
        """Load the base CSS styles with system font detection."""
        # First load system-aware CSS
        self._load_system_css()

        css_dir = Path(__file__).parent / "resources" / "css"
        base_css_path = css_dir / "style.css"

        if base_css_path.exists():
            try:
                self.css_provider.load_from_path(str(base_css_path))
                self._add_provider_to_screen(self.css_provider)
                logger.info("Loaded base CSS from %s", base_css_path)
            except GLib.Error as e:
                logger.warning("Error loading base CSS: %s", e)
        else:
            logger.warning("Base CSS file not found at %s", base_css_path)

    def _load_system_css(self):
        """Generate and load CSS with proper font scaling based on DPI settings."""
        try:
            # Calculate effective DPI scale
            effective_scale = self._calculate_effective_dpi_scale()

            # Generate CSS with scaled fonts
            css_content = self._generate_scaled_css(effective_scale)

            # Apply the generated CSS
            self.system_css_provider.load_from_data(css_content.encode())
            self._add_provider_to_screen(self.system_css_provider)

        except Exception as e:
            logger.warning("Could not load system CSS with font scaling: %s", e)

    def load_theme(self, theme_name: str):
        """Load a specific theme (light/dark)."""
        css_dir = Path(__file__).parent / "resources" / "css"
        theme_css_path = css_dir / f"{theme_name}-theme.css"

        if theme_css_path.exists():
            try:
                # Remove old theme provider
                screen = Gdk.Screen.get_default()
                context = Gtk.StyleContext()
                context.remove_provider_for_screen(screen, self.theme_provider)

                # Load new theme
                self.theme_provider = Gtk.CssProvider()
                self.theme_provider.load_from_path(str(theme_css_path))
                self._add_provider_to_screen(self.theme_provider)

                self.current_theme = theme_name

                # Reload system CSS after theme to ensure transparency overrides
                self._load_system_css()

                logger.info("Loaded %s theme from %s", theme_name, theme_css_path)
            except GLib.Error as e:
                logger.warning("Error loading %s theme: %s", theme_name, e)
        else:
            logger.warning("Theme file not found at %s", theme_css_path)

    def toggle_theme(self):
        """Toggle between light and dark theme."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.load_theme(new_theme)

    def _add_provider_to_screen(self, provider):
        """Helper to add CSS provider to screen."""
        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        # Use APPLICATION priority (800) which is higher than theme (600) to ensure our CSS overrides Adwaita
        priority = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        context.add_provider_for_screen(
            screen,
            provider,
            priority
        )

    def _detect_system_theme(self):
        """Detect the system's preferred theme (light/dark)."""
        try:
            settings = Gtk.Settings.get_default()

            # Try to get the dark theme preference
            prefer_dark = settings.get_property("gtk-application-prefer-dark-theme")
            if prefer_dark:
                logger.info("Detected system preference: dark theme")
                return "dark"

            # Fallback: check the theme name for dark indicators
            theme_name = settings.get_property("gtk-theme-name") or ""
            theme_name_lower = theme_name.lower()

            if any(dark_indicator in theme_name_lower for dark_indicator in ["dark", "noir", "black", "adwaita-dark"]):
                logger.info("Detected dark theme from theme name: %s", theme_name)
                return "dark"

            logger.info("Detected light theme (theme name: %s)", theme_name)
            return "light"

        except Exception as e:
            logger.warning("Could not detect system theme preference: %s", e)
            logger.info("Falling back to light theme")
            return "light"

    def _calculate_effective_dpi_scale(self):
        """Calculate the effective DPI scale factor using priority: CLI > ENV > Config > Auto."""
        try:
            # Priority 1: Command-line override
            if self._override_dpi:
                return float(self._override_dpi) / 96.0

            # Priority 2: Environment variable
            env_dpi = os.environ.get('TST_DPI')
            if env_dpi:
                try:
                    return float(env_dpi) / 96.0
                except ValueError:
                    logger.warning("Invalid TST_DPI value %r, ignoring", env_dpi)

            # Priority 3: Configuration file
            if self._config_dpi_scale != "auto":
                if isinstance(self._config_dpi_scale, int | float):
                    return float(self._config_dpi_scale)
                elif isinstance(self._config_dpi_scale, str):
                    try:
                        return float(self._config_dpi_scale)
                    except ValueError:
                        logger.warning("Invalid dpi_scale value %r, using auto", self._config_dpi_scale)

            # Priority 4: Auto-detection
            return self._detect_system_dpi_scale()

        except Exception as e:
            logger.warning("Error calculating DPI scale, using 1.0: %s", e)
            return 1.0

    def _detect_system_dpi_scale(self):
        """Auto-detect system DPI scale factor with comfort scaling for high-DPI displays."""
        try:
            # Initialize GTK to get settings
            settings = Gtk.Settings.get_default()
            screen = Gdk.Screen.get_default()

            # Get system DPI
            dpi = settings.get_property("gtk-xft-dpi")
            system_dpi = dpi / 1024.0 if dpi else None

            # Get monitor DPI using reliable detection method (same as font test)
            monitor_dpi = 96.0  # Default
            if screen:
                try:
                    display = screen.get_display()
                    monitor = display.get_primary_monitor() or display.get_monitor(0)
                    geometry = monitor.get_geometry()
                    width = geometry.width
                    height = geometry.height
                    width_mm = monitor.get_width_mm()
                    height_mm = monitor.get_height_mm()

                    if width_mm > 0 and height_mm > 0:
                        dpi_x = (width * 25.4) / width_mm
                        dpi_y = (height * 25.4) / height_mm
                        monitor_dpi = (dpi_x + dpi_y) / 2
                except (AttributeError, TypeError, ValueError) as e:
                    logger.debug("Could not detect monitor DPI: %s", e)

            # Choose the more appropriate DPI source
            # For high-DPI displays, prioritize monitor DPI over conservative GTK settings
            if monitor_dpi > 150 and system_dpi and system_dpi < monitor_dpi * 0.8:
                # Monitor DPI is high and system DPI seems conservative, use monitor DPI
                effective_dpi = monitor_dpi
            elif system_dpi and system_dpi > 96:
                # Use system DPI if it's reasonable
                effective_dpi = system_dpi
            else:
                # Fall back to monitor DPI
                effective_dpi = monitor_dpi

            # Calculate base scale factor
            base_scale = effective_dpi / 96.0

            # Apply comfort scaling for better readability on high-DPI displays
            if 240 <= effective_dpi <= 260:  # Calibrated for ~250 DPI displays (MacBook-style)
                # Provide optimal 2.0x scaling for this DPI range
                comfort_scale = 2.0
            elif effective_dpi >= 180:  # High-DPI (4K+ monitors)
                # Ensure at least 1.8x scaling for very high DPI displays
                comfort_scale = max(base_scale, 1.8)
            elif effective_dpi >= 120:  # Medium-high DPI (1440p monitors)
                # Ensure at least 1.25x scaling for medium-high DPI
                comfort_scale = max(base_scale, 1.25)
            else:
                # Standard DPI, use base scale but ensure minimum 1.0
                comfort_scale = max(base_scale, 1.0)

            return comfort_scale

        except Exception as e:
            logger.warning("Could not detect system DPI, using scale 1.0: %s", e)
            return 1.0

    def _generate_scaled_css(self, scale_factor):
        """Generate CSS with scaled font sizes."""
        try:
            # Get system font information
            settings = Gtk.Settings.get_default()
            font_name = settings.get_property("gtk-font-name") or "Sans 10"

            # Parse base font size
            font_parts = font_name.split()
            try:
                base_font_size = float(font_parts[-1])
            except (ValueError, IndexError):
                base_font_size = 10.0

            # Calculate scaled sizes with minimums
            effective_dpi = scale_factor * 96.0
            if effective_dpi >= 180:
                min_ui_size = 14
                min_terminal_size = 15
            else:
                min_ui_size = 10
                min_terminal_size = 11

            ui_font_size = max(int(base_font_size * scale_factor), min_ui_size)
            terminal_font_size = max(int((base_font_size + 1) * scale_factor), min_terminal_size)

            # Generate CSS
            css_content = f"""
/* Auto-generated system CSS with DPI scaling */
window {{
    font-size: {ui_font_size}px;
}}

.sidebar {{
    font-size: {ui_font_size}px;
}}

.terminal {{
    font-size: {terminal_font_size}px;
}}

headerbar {{
    font-size: {ui_font_size}px;
}}

button {{
    font-size: {ui_font_size}px;
}}

treeview {{
    font-size: {ui_font_size}px;
}}

/* Additional scaling for high-DPI displays */
label {{
    font-size: {ui_font_size}px;
}}

entry {{
    font-size: {ui_font_size}px;
}}
"""
            css_content += self._generate_sidebar_transparency_css()

            if scale_factor > 1.0:
                logger.info(
                    "Applied font scaling: %.2fx (UI: %spx, Terminal: %spx)",
                    scale_factor,
                    ui_font_size,
                    terminal_font_size,
                )

            return css_content

        except Exception as e:
            logger.warning("Error generating scaled CSS: %s", e)
            return "/* Error generating scaled CSS */"

    def _generate_sidebar_transparency_css(self):
        """Generate runtime CSS for sidebar transparency from terminal config."""
        try:
            alpha = float(config_manager.get("terminal.transparency", 1.0))
        except (TypeError, ValueError):
            alpha = 1.0

        alpha = max(0.0, min(alpha, 1.0))

        if self.current_theme == "dark":
            sidebar_rgb = (37, 37, 37)
            border_color = "#404040"
            selected_color = "#4a9eff"
            hover_color = "rgba(74, 158, 255, 0.15)"
        else:
            sidebar_rgb = (248, 248, 248)
            border_color = "#dddddd"
            selected_color = "#0066cc"
            hover_color = "rgba(0, 102, 204, 0.08)"

        r, g, b = sidebar_rgb
        return f"""

/* Runtime sidebar transparency; loaded after theme CSS. */
.sidebar,
.sidebar-transparency-root,
revealer.sidebar-transparency-root {{
    background-color: rgba({r}, {g}, {b}, {alpha:.3f});
    background-image: none;
}}

.sidebar {{
    border-right: 1px solid {border_color};
}}

.sidebar box,
.sidebar .sidebar-header,
.sidebar scrolledwindow,
.sidebar viewport,
.sidebar treeview,
.sidebar treeview.view,
.sidebar .sidebar-tree,
.sidebar .transparent-scroll,
.sidebar .transparent-tree,
.sidebar-tree,
.sidebar-tree box,
.sidebar-tree scrolledwindow,
.sidebar-tree viewport,
.sidebar-tree treeview,
.sidebar-tree treeview.view,
.transparent-scroll,
.transparent-scroll viewport,
.transparent-tree,
treeview.transparent-tree,
treeview.transparent-tree.view {{
    background-color: transparent;
    background-image: none;
}}

.sidebar treeview:selected,
.sidebar treeview.view:selected,
.sidebar treeview.view:selected:focus,
.sidebar-tree row:selected,
.sidebar-tree cell:selected {{
    background-color: {selected_color};
    color: white;
}}

.sidebar treeview row:hover,
.sidebar treeview.view row:hover {{
    background-color: {hover_color};
}}
"""
