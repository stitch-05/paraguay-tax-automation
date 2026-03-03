"""Utility functions for the tax automation script."""

import random
import threading
import time
from typing import Optional, TypeVar


T = TypeVar('T')


class AnimatedWaitContext:
    """Context manager for animated waiting during operations."""

    _context_stack = []

    def __init__(self, message: str, verbose: bool = True, debug: bool = False, mockup_mode: bool = False):
        """
        Initialize animated wait context.

        Args:
            message: Message to display with animation
            verbose: Whether to show the animation (message always shows)
            debug: If True, show wait info but skip enforced random delay
            mockup_mode: If True, skip actual sleeping but keep displaying seconds
        """
        self.message = message
        self.verbose = verbose
        self.debug = debug
        self.mockup_mode = mockup_mode
        self.sleep_time = random.randint(1, 4)  # Random wait time like animated_wait
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._start_time: Optional[float] = None
        self.failed = False
        self._message_printed = False

    def mark_failed(self):
        """Mark this wait context as failed."""
        self.failed = True

    def suppress_completion_message(self):
        """Suppress the completion message (error was already printed)."""
        self._message_printed = True

    def print_completion_now(self, failed: bool = True):
        """Stop animation and print completion line immediately."""
        if self._thread and not self._message_printed:
            # Stop the animation thread
            self._stop_event.set()
            self._thread.join(timeout=0.1)

            # Print completion line
            icon = 'x' if failed else '✓'
            if self.verbose:
                print(f'\r{self.message} (waiting {self.sleep_time}s)... {icon}')
            else:
                print(f'\r{self.message}... {icon}')

            # Mark as printed so __exit__ doesn't duplicate
            self._message_printed = True
            self.failed = failed

    @classmethod
    def mark_current_failed(cls):
        """Mark the current active wait context as failed."""
        if cls._context_stack:
            cls._context_stack[-1].mark_failed()

    @classmethod
    def suppress_current_completion(cls):
        """Suppress completion message for current context (error already printed)."""
        if cls._context_stack:
            cls._context_stack[-1].suppress_completion_message()

    @classmethod
    def print_current_completion(cls, failed: bool = True):
        """Print completion line immediately for current context."""
        if cls._context_stack:
            cls._context_stack[-1].print_completion_now(failed)

    def _animate(self):
        """Run the animation in a background thread."""
        dot_count = 0
        while not self._stop_event.is_set():
            dots = '.' * ((dot_count % 3) + 1)
            spaces = ' ' * (3 - len(dots))
            # Show sleep time if verbose (before dots)
            if self.verbose:
                time_info = f' (waiting {self.sleep_time}s)'
                print(f'\r{self.message}{time_info}{dots}{spaces}', end='', flush=True)
            else:
                print(f'\r{self.message}{dots}{spaces}', end='', flush=True)
            dot_count += 1
            time.sleep(0.5)

    def __enter__(self):
        """Start the animation."""
        # Record start time and start animation thread immediately
        self._start_time = time.time()

        # In mockup mode, skip animation
        if self.mockup_mode:
            print(f'{self.message}...', end='', flush=True)
        else:
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
            self.__class__._context_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the animation."""
        if self.mockup_mode:
            # In mockup mode without animation, overwrite the static message
            icon = '✓' if exc_type is None and not self.failed else 'x'
            print(f'\r{self.message}... {icon}')
            self._message_printed = True
        elif self._thread and self._start_time:
            # Calculate elapsed time and sleep for the remainder if needed
            elapsed = time.time() - self._start_time
            # Skip sleep in debug mode
            remaining = 0 if self.debug else max(0, self.sleep_time - elapsed)
            if remaining > 0:
                time.sleep(remaining)

            self._stop_event.set()
            self._thread.join(timeout=0.1)

        if self.__class__._context_stack and self.__class__._context_stack[-1] is self:
            self.__class__._context_stack.pop()
        elif self in self.__class__._context_stack:
            self.__class__._context_stack.remove(self)

        # Only print completion message if not already printed
        if not self._message_printed:
            icon = '✓' if exc_type is None and not self.failed else 'x'
            if self.verbose:
                print(f'\r{self.message} (waiting {self.sleep_time}s)... {icon}')
            else:
                print(f'\r{self.message}... {icon}')


def send_message(notifier, title: str, message: str, message_prefix: str = '', mockup_mode: bool = False) -> None:
    """Print a local log line and send notification."""
    print(f'{title} - {message}')
    full_message = f'{message_prefix}{message}'

    # Send notification with animated wait only if a real notification service is configured
    from notifications import NoopNotifier
    from unittest.mock import MagicMock

    if isinstance(notifier, NoopNotifier):
        notifier.send(title, full_message)
    elif isinstance(notifier, MagicMock):
        # In tests with mock notifier, skip animation entirely for speed
        print('Sending notification... ✓')
        notifier.send(title, full_message)
    else:
        # Real notification service - show animation, no enforced minimum wait
        with AnimatedWaitContext('Sending notification', verbose=False):
            notifier.send(title, full_message)
