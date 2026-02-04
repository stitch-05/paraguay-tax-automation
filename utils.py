"""Utility functions for the tax automation script."""

import random
import threading
import time
from typing import Callable, Optional, TypeVar


T = TypeVar('T')


class AnimatedWaitContext:
    """Context manager for animated waiting during operations."""

    def __init__(self, message: str, verbose: bool = True):
        """
        Initialize animated wait context.

        Args:
            message: Message to display with animation
            verbose: Whether to show the animation (message always shows)
        """
        self.message = message
        self.verbose = verbose
        self.sleep_time = random.randint(1, 4)  # Random wait time like animated_wait
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

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
        # Start animation thread immediately (it will print the message)
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the animation."""
        if self._thread:
            self._stop_event.set()
            self._thread.join(timeout=2.0)
            # Print final state with 3 dots and checkmark on same line
            # Include padding to clear any remaining text from verbose mode
            if self.verbose:
                # Clear the waiting info by including it in the final print
                print(f'\r{self.message} (waiting {self.sleep_time}s)... ✓')
            else:
                print(f'\r{self.message}... ✓')


def send_message(notifier, title: str, message: str, message_prefix: str = '') -> None:
    """Print a local log line and send notification."""
    print(f'{title} - {message}')
    full_message = f'{message_prefix}{message}'
    notifier.send(title, full_message)
