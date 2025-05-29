#!/usr/bin/env python3
"""
Demonstration script for Milestone 2 - Terminal Embedding

This script shows the VTE terminal functionality in a simple window.
"""

import sys
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")

from gi.repository import Gtk, GLib
from src.tree_style_terminal.widgets.terminal import VteTerminal


class DemoWindow(Gtk.Window):
    """Simple demo window with VTE terminal."""
    
    def __init__(self):
        super().__init__(title="VTE Terminal Demo")
        self.set_default_size(800, 600)
        
        # Create vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)
        
        # Create header bar
        header = Gtk.HeaderBar()
        header.set_title("Terminal Demo")
        header.set_show_close_button(True)
        self.set_titlebar(header)
        
        # Add new terminal button
        new_btn = Gtk.Button.new_with_label("New Terminal")
        new_btn.connect("clicked", self.on_new_terminal)
        header.pack_start(new_btn)
        
        # Create stack for terminals
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        vbox.pack_start(self.stack, True, True, 0)
        
        # Terminal counter
        self.terminal_count = 0
        
        # Create first terminal
        self.create_terminal()
        
        # Connect close signal
        self.connect("destroy", Gtk.main_quit)
    
    def create_terminal(self):
        """Create a new terminal."""
        self.terminal_count += 1
        terminal_id = f"terminal_{self.terminal_count}"
        
        terminal = VteTerminal()
        if terminal.spawn_shell():
            self.stack.add_titled(terminal, terminal_id, f"Terminal {self.terminal_count}")
            self.stack.set_visible_child(terminal)
            terminal.show_all()
            print(f"Created {terminal_id}")
        else:
            print(f"Failed to create {terminal_id}")
    
    def on_new_terminal(self, button):
        """Handle new terminal button."""
        self.create_terminal()


def main():
    """Run the demo."""
    window = DemoWindow()
    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()

## Milestone 2 Implementation Complete!

I have successfully implemented **Milestone 2 - Terminal Embedding** according to the specifications in your TODO and ARCHITECTURE documents. Here's what was accomplished:

### ✅ Completed Tasks

1. **VTE Dependency**: 
   - VTE 2.91 (GTK3) is available and working
   - No additional Python package needed (system library)

2. **Terminal Widget**:
   - Created `widgets/terminal.py` with `VteTerminal` class
   - Embeds `Vte.Terminal` in a `Gtk.Box` container
   - Includes scrolled window for proper display

3. **Spawn Function**:
   - Implemented `spawn_shell(argv=None, cwd=None)` method
   - Uses `$SHELL` environment variable, falls back to `/bin/bash`
   - Proper error handling and logging

4. **Layout Integration**:
   - Integrated terminal widget into `MainWindow`
   - Terminal displays centrally when created
   - Stack-based terminal switching system

5. **Basic Configuration**:
   - `set_font_size()` method for font configuration
   - `set_scrollback_length()` method for buffer size
   - Default monospace font and reasonable scrollback

### 🚀 How to Test the Implementation

**Option 1: Run the main application:**
```bash
cd tree-style-terminal
python -m src.tree_style_terminal.main
```

**Option 2: Run the demo script:**
```bash
cd tree-style-terminal
python demo_milestone2.py
```

**Option 3: Run verification tests:**
```bash
cd tree-style-terminal
python verify_milestone2.py
```

### 🔧 Key Features Working

- VTE terminal widget creation and display
- Shell spawning with proper environment
- Font and scrollback configuration
- Terminal lifecycle management (create/close)
- Error handling for failed terminal creation
- Integration with GTK3 application stack

The terminal should now display a fully functional shell where you can run commands, navigate directories, and use all standard terminal features. Click the "New Terminal" button in the header bar to create additional terminal sessions.

Please test the application and let me know if you'd like me to continue with the next milestone or make any adjustments!