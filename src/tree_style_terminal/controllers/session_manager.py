"""
Session manager for high-level session operations.

Provides a high-level API for creating, closing, and managing terminal sessions,
and maintains the current session selection state.
"""

from __future__ import annotations

import logging
import os
from typing import Optional, Callable, Dict

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import GLib

from ..models.session import TerminalSession
from ..models.tree import SessionTree
from ..widgets.terminal import VteTerminal

logger = logging.getLogger(__name__)


class SessionManager:
    """
    High-level API for session management.
    
    Manages terminal session creation, destruction, and selection state.
    Coordinates between the SessionTree model and VTE terminal widgets.
    """
    
    def __init__(self, session_tree: SessionTree) -> None:
        """
        Initialize the session manager.
        
        Args:
            session_tree: The SessionTree model to manage
        """
        self.session_tree = session_tree
        self.current_session: Optional[TerminalSession] = None
        
        # Map sessions to their VTE terminal widgets
        self._session_terminals: Dict[TerminalSession, VteTerminal] = {}
        
        # Callbacks for session events
        self._session_created_callback: Optional[Callable[[TerminalSession, VteTerminal], None]] = None
        self._session_closed_callback: Optional[Callable[[TerminalSession, list[TerminalSession], Optional[TerminalSession]], None]] = None
        self._session_selected_callback: Optional[Callable[[TerminalSession], None]] = None
        
        # Counter for generating unique session IDs
        self._session_counter = 0
        
        logger.debug("SessionManager initialized")
    
    def new_session(
        self, 
        parent: Optional[TerminalSession] = None,
        cwd: Optional[str] = None,
        title: Optional[str] = None
    ) -> Optional[TerminalSession]:
        """
        Create a new terminal session.
        
        Args:
            parent: Parent session for hierarchy, None for root level
            cwd: Working directory for the new session
            title: Custom title for the session
            
        Returns:
            The created TerminalSession, or None if creation failed
        """
        try:
            # Generate unique session identifier
            self._session_counter += 1
            
            # Determine working directory
            if cwd is None:
                if parent and parent.cwd:
                    cwd = parent.cwd
                else:
                    cwd = os.path.expanduser("~")
            
            # Create VTE terminal widget
            terminal_widget = VteTerminal()
            
            # Spawn shell in the terminal
            if not terminal_widget.spawn_shell(cwd=cwd):
                logger.error("Failed to spawn shell for new session")
                terminal_widget.destroy()
                return None
            
            # Use counter as placeholder PTY fd (actual PTY is managed by VTE internally)
            pty_fd = self._session_counter
            
            # Create session object
            session = TerminalSession(
                pid=self._session_counter,  # Use counter as temporary PID
                pty_fd=pty_fd,
                cwd=cwd,
                title=title
            )
            
            # Store terminal widget reference
            self._session_terminals[session] = terminal_widget
            
            # Connect terminal signals (use the actual VTE terminal, not the wrapper)
            terminal_widget.terminal.connect("child-exited", self._on_terminal_exited, session)
            terminal_widget.terminal.connect("window-title-changed", self._on_terminal_title_changed, session)
            
            # Add to session tree
            self.session_tree.add_node(session, parent)
            
            # Set as current session
            self.current_session = session
            
            # Notify callbacks
            if self._session_created_callback:
                self._session_created_callback(session, terminal_widget)
            
            logger.info(f"Created new session: {session.title}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    def new_child(self, title: Optional[str] = None) -> Optional[TerminalSession]:
        """
        Create a new child session under the current session.
        
        Args:
            title: Custom title for the session
            
        Returns:
            The created TerminalSession, or None if creation failed
        """
        if not self.current_session:
            logger.warning("No current session to create child under")
            return self.new_session(title=title)
        
        return self.new_session(
            parent=self.current_session,
            cwd=self.current_session.cwd,
            title=title
        )
    
    def new_sibling(self, title: Optional[str] = None) -> Optional[TerminalSession]:
        """
        Create a new sibling session at the same level as current session.
        
        Args:
            title: Custom title for the session
            
        Returns:
            The created TerminalSession, or None if creation failed
        """
        if not self.current_session:
            return self.new_session(title=title)
        
        parent = self.session_tree.get_parent(self.current_session)
        return self.new_session(
            parent=parent,
            cwd=self.current_session.cwd,
            title=title
        )
    
    def close_session(self, session: TerminalSession) -> None:
        """
        Close a terminal session.
        
        Args:
            session: The session to close
        """
        try:
            # Collect adoption information BEFORE removing from tree
            children_to_adopt = session.children.copy() if session.children else []
            parent_session = self.session_tree.get_parent(session)
            
            # Get terminal widget
            terminal_widget = self._session_terminals.get(session)
            if terminal_widget:
                # Close the terminal
                terminal_widget.close()
                del self._session_terminals[session]
            
            # Remove from session tree (this triggers adoption)
            self.session_tree.remove_node(session)
            
            # Update current session if needed
            if self.current_session == session:
                # Try to select the best alternative session
                # Priority order: 1) Parent, 2) First child, 3) Any root
                if parent_session and parent_session in self._session_terminals:
                    self.select_session(parent_session)
                elif children_to_adopt and children_to_adopt[0] in self._session_terminals:
                    self.select_session(children_to_adopt[0])
                else:
                    roots = self.session_tree.get_roots()
                    if roots:
                        self.select_session(roots[0])
                    else:
                        self.current_session = None
            
            # Notify callbacks with adoption information
            if self._session_closed_callback:
                self._session_closed_callback(session, children_to_adopt, parent_session)
            
            logger.info(f"Closed session: {session.title}")
            
        except Exception as e:
            logger.error(f"Error closing session {session.title}: {e}")
    
    def close_current_session(self) -> None:
        """Close the currently selected session."""
        if self.current_session:
            self.close_session(self.current_session)
    
    def select_session(self, session: TerminalSession) -> None:
        """
        Select a session as the current active session.
        
        Args:
            session: The session to select
        """
        if session in self._session_terminals:
            self.current_session = session
            
            # Notify callbacks
            if self._session_selected_callback:
                self._session_selected_callback(session)
            
            logger.debug(f"Selected session: {session.title}")
        else:
            logger.warning(f"Session not found: {session}")
    
    def get_terminal_widget(self, session: TerminalSession) -> Optional[VteTerminal]:
        """
        Get the VTE terminal widget for a session.
        
        Args:
            session: The session to get the terminal for
            
        Returns:
            The VteTerminal widget, or None if not found
        """
        return self._session_terminals.get(session)
    
    def get_all_sessions(self) -> list[TerminalSession]:
        """Get a list of all active sessions."""
        return list(self._session_terminals.keys())
    
    def _on_terminal_exited(self, terminal: VteTerminal, exit_status: int, session: TerminalSession) -> None:
        """
        Handle terminal process exit.
        
        Args:
            terminal: The VTE terminal widget
            exit_status: Exit status of the process
            session: The associated session
        """
        logger.info(f"Terminal exited with status {exit_status}: {session.title}")
        
        # Auto-close the session when terminal exits
        GLib.idle_add(lambda: self.close_session(session))
    
    def _on_terminal_title_changed(self, vte_terminal, session: TerminalSession) -> None:
        """
        Handle terminal title changes and update session CWD.
        
        Args:
            vte_terminal: The native VTE terminal widget
            session: The associated session
        """
        # Get our VteTerminal wrapper from the session
        terminal_widget = self._session_terminals.get(session)
        if not terminal_widget:
            logger.warning(f"Terminal widget not found for session: {session}")
            return
        
        # Update terminal title
        raw_title = terminal_widget.get_window_title()
        if raw_title:
            # Parse and format the terminal title
            parsed_title = session.parse_terminal_title(raw_title)
            title_changed = parsed_title != session.title
            if title_changed:
                session.title = parsed_title
                logger.debug(f"Updated session title: {parsed_title}")
        else:
            title_changed = False
        
        # Update current working directory
        current_dir = terminal_widget.get_current_directory()
        cwd_changed = current_dir and current_dir != session.cwd
        if cwd_changed:
            session.cwd = current_dir
            logger.debug(f"Updated session CWD: {current_dir}")
            
            # If no terminal title was processed, update title from CWD
            if not raw_title:
                new_dir_title = session._get_short_path_title(current_dir)
                if new_dir_title != session.title:
                    session.title = new_dir_title
                    title_changed = True
                    logger.debug(f"Updated session title from CWD: {new_dir_title}")
        
        # Notify sidebar of changes if any updates occurred
        if title_changed or cwd_changed:
            if hasattr(self, 'session_changed_callback') and self.session_changed_callback:
                self.session_changed_callback(session)
    
    def set_session_created_callback(self, callback: Callable[[TerminalSession, VteTerminal], None]) -> None:
        """Set callback for when a session is created."""
        self._session_created_callback = callback
    
    def set_session_changed_callback(self, callback: Callable[[TerminalSession], None]) -> None:
        """Set callback for when a session's properties change."""
        self.session_changed_callback = callback
    
    def set_session_closed_callback(self, callback: Callable[[TerminalSession, list[TerminalSession], Optional[TerminalSession]], None]) -> None:
        """Set callback for when a session is closed."""
        self._session_closed_callback = callback
    
    def set_session_selected_callback(self, callback: Callable[[TerminalSession], None]) -> None:
        """Set callback for when a session is selected."""
        self._session_selected_callback = callback
    
    def select_next_session(self) -> None:
        """Select the next session in the session list."""
        all_sessions = self.get_all_sessions()
        if len(all_sessions) <= 1:
            return
        
        if not self.current_session:
            if all_sessions:
                self.select_session(all_sessions[0])
            return
        
        try:
            current_index = all_sessions.index(self.current_session)
            next_index = (current_index + 1) % len(all_sessions)
            self.select_session(all_sessions[next_index])
            logger.debug(f"Selected next session: {all_sessions[next_index].title}")
        except ValueError:
            logger.warning("Current session not found in session list")
    
    def select_previous_session(self) -> None:
        """Select the previous session in the session list."""
        all_sessions = self.get_all_sessions()
        if len(all_sessions) <= 1:
            return
        
        if not self.current_session:
            if all_sessions:
                self.select_session(all_sessions[-1])
            return
        
        try:
            current_index = all_sessions.index(self.current_session)
            prev_index = (current_index - 1) % len(all_sessions)
            self.select_session(all_sessions[prev_index])
            logger.debug(f"Selected previous session: {all_sessions[prev_index].title}")
        except ValueError:
            logger.warning("Current session not found in session list")
    
    def get_session_count(self) -> int:
        """Get the number of active sessions."""
        return len(self._session_terminals)