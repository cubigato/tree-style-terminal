#!/usr/bin/env python3
"""
Demonstration script for the SidebarController TreeStore functionality.

This script shows how the SidebarController manages a Gtk.TreeStore
with session objects and titles, and how it synchronizes with a SessionTree.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

from src.tree_style_terminal.controllers.sidebar import SidebarController
from src.tree_style_terminal.models.session import TerminalSession
from src.tree_style_terminal.models.tree import SessionTree


def create_sample_sessions():
    """Create a sample session tree structure for demonstration."""
    session_tree = SessionTree()
    
    # Create some sample sessions
    root1 = TerminalSession(pid=1001, pty_fd=10, cwd="/home/user")
    root2 = TerminalSession(pid=1002, pty_fd=11, cwd="/var/log")
    
    child1 = TerminalSession(pid=1003, pty_fd=12, cwd="/home/user/projects")
    child2 = TerminalSession(pid=1004, pty_fd=13, cwd="/home/user/documents")
    
    grandchild = TerminalSession(pid=1005, pty_fd=14, cwd="/home/user/projects/myapp")
    
    # Build the tree structure
    session_tree.add_node(root1)
    session_tree.add_node(root2)
    session_tree.add_node(child1, root1)
    session_tree.add_node(child2, root1)
    session_tree.add_node(grandchild, child1)
    
    return session_tree


def print_tree_store_contents(controller):
    """Print the contents of the TreeStore for inspection."""
    print("\n--- TreeStore Contents ---")
    
    def print_iter(tree_iter, depth=0):
        if tree_iter is None:
            return
        
        indent = "  " * depth
        session = controller.tree_store.get_value(tree_iter, controller.COL_OBJECT)
        title = controller.tree_store.get_value(tree_iter, controller.COL_TITLE)
        
        print(f"{indent}{title} (PID: {session.pid})")
        
        # Print children
        child_iter = controller.tree_store.iter_children(tree_iter)
        while child_iter:
            print_iter(child_iter, depth + 1)
            child_iter = controller.tree_store.iter_next(child_iter)
    
    # Start with root nodes
    root_iter = controller.tree_store.get_iter_first()
    while root_iter:
        print_iter(root_iter)
        root_iter = controller.tree_store.iter_next(root_iter)


def demo_basic_functionality():
    """Demonstrate basic SidebarController functionality."""
    print("=== SidebarController Demo ===")
    
    # Create sample data
    session_tree = create_sample_sessions()
    
    # Create controller
    controller = SidebarController(session_tree)
    
    print(f"TreeStore has {len(controller.tree_store)} root items")
    print(f"TreeStore has {controller.tree_store.get_n_columns()} columns")
    
    # Print initial contents
    print_tree_store_contents(controller)
    
    # Demo: Add a new session
    print("\n--- Adding new session ---")
    new_session = TerminalSession(pid=2001, pty_fd=20, cwd="/tmp")
    controller.add_session(new_session)
    
    print_tree_store_contents(controller)
    
    # Demo: Update a session title
    print("\n--- Updating session title ---")
    controller.update_session_title(new_session, "Temporary Files")
    
    print_tree_store_contents(controller)
    
    # Demo: Remove a session
    print("\n--- Removing session ---")
    controller.remove_session(new_session)
    
    print_tree_store_contents(controller)
    
    # Demo: Find session by iter
    print("\n--- Finding sessions ---")
    root_iter = controller.tree_store.get_iter_first()
    found_session = controller.get_session_from_iter(root_iter)
    print(f"Session from first iter: {found_session.title} (PID: {found_session.pid})")
    
    # Find iter for session
    found_iter = controller.find_iter_for_session(found_session)
    retrieved_session = controller.get_session_from_iter(found_iter)
    print(f"Round-trip successful: {retrieved_session == found_session}")


def demo_sync_functionality():
    """Demonstrate synchronization with SessionTree changes."""
    print("\n=== Sync Demo ===")
    
    # Create empty tree and controller
    session_tree = SessionTree()
    controller = SidebarController(session_tree)
    
    print("Starting with empty tree:")
    print(f"TreeStore has {len(controller.tree_store)} items")
    
    # Modify the session tree directly (simulating external changes)
    session1 = TerminalSession(pid=3001, pty_fd=30, cwd="/external1")
    session2 = TerminalSession(pid=3002, pty_fd=31, cwd="/external2")
    
    session_tree.add_node(session1)
    session_tree.add_node(session2, session1)
    
    print(f"After modifying SessionTree directly: TreeStore still has {len(controller.tree_store)} items")
    
    # Sync to update TreeStore
    controller.sync_with_session_tree()
    
    print(f"After sync: TreeStore has {len(controller.tree_store)} items")
    print_tree_store_contents(controller)


if __name__ == "__main__":
    # Run demonstrations
    demo_basic_functionality()
    demo_sync_functionality()
    
    print("\n=== Demo Complete ===")
    print("The SidebarController successfully manages TreeStore with [object, title] columns")
    print("and provides methods for synchronization with SessionTree.")