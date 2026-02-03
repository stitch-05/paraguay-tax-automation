"""Notification services for file-taxes-paraguay."""

import smtplib
import ssl
import subprocess
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional


class Notifier(ABC):
    """Abstract base class for notification services."""

    @abstractmethod
    def send(self, title: str, message: str) -> bool:
        """
        Send a notification.

        Args:
            title: Notification title
            message: Notification message

        Returns:
            True if successful, False otherwise
        """
        pass


class PushoverNotifier(Notifier):
    """Pushover notification service."""

    API_URL = 'https://api.pushover.net/1/messages.json'

    def __init__(self, token: str, user: str):
        self.token = token
        self.user = user

    def send(self, title: str, message: str) -> bool:
        if not self.token or not self.user:
            print('Pushover: Missing token or user')
            return False

        data = {
            'token': self.token,
            'user': self.user,
            'title': title,
            'message': message,
            'html': '1',
        }

        encoded_data = urllib.parse.urlencode(data).encode('utf-8')

        try:
            req = urllib.request.Request(self.API_URL, data=encoded_data)
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.status == 200
        except Exception as e:
            print(f'Pushover error: {e}')
            return False


class SignalNotifier(Notifier):
    """Signal notification service via signal-cli."""

    def __init__(self, sender: str, recipient: str):
        self.sender = sender
        self.recipient = recipient

    def send(self, title: str, message: str) -> bool:
        if not self.sender or not self.recipient:
            print('Signal: Missing sender or recipient')
            return False

        # Combine title and message for Signal
        full_message = f'{title}\n{message}'

        try:
            result = subprocess.run(
                ['signal-cli', '-a', self.sender, 'send', '-m', full_message, self.recipient],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                print(f'Signal error: {result.stderr}')
                return False
            return True
        except FileNotFoundError:
            print('Signal error: signal-cli not found')
            return False
        except subprocess.TimeoutExpired:
            print('Signal error: Timeout')
            return False
        except Exception as e:
            print(f'Signal error: {e}')
            return False


class EmailNotifier(Notifier):
    """Email notification service via SMTP."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        addr: str,
        password: str,
        recipients: List[str]
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.addr = addr
        self.password = password
        self.recipients = recipients

    def send(self, title: str, message: str) -> bool:
        if not self.smtp_host or not self.recipients:
            print('Email: Missing SMTP host or recipients')
            return False

        msg = MIMEMultipart()
        msg['From'] = self.addr
        msg['To'] = ', '.join(self.recipients)
        msg['Subject'] = title
        msg.attach(MIMEText(message, 'plain'))

        try:
            if self.password:
                # Try TLS first
                try:
                    server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                    server.starttls(context=ssl.create_default_context())
                except Exception:
                    # Fallback to SSL
                    server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
                server.login(self.addr, self.password)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)

            server.sendmail(self.addr, self.recipients, msg.as_string())
            server.quit()
            print(f'Email sent: {self.addr} --> {self.recipients}')
            return True
        except Exception as e:
            print(f'Email error: {e}')
            return False


class NoopNotifier(Notifier):
    """No-op notifier that just prints messages."""

    def send(self, title: str, message: str) -> bool:
        print(f'MSG: {title} {message}')
        return True


def get_notifier(
    service: Optional[str],
    pushover_token: str = '',
    pushover_user: str = '',
    signal_user: str = '',
    signal_recipient: str = '',
    smtp_host: str = '',
    smtp_port: int = 587,
    smtp_addr: str = '',
    smtp_pwd: str = '',
    smtp_recv: str = ''
) -> Notifier:
    """
    Factory function to get the appropriate notifier.

    Args:
        service: The notification service name ('pushover', 'signal', 'email')
        Other args: Service-specific configuration

    Returns:
        A Notifier instance
    """
    if service == 'pushover':
        return PushoverNotifier(pushover_token, pushover_user)
    elif service == 'signal':
        return SignalNotifier(signal_user, signal_recipient)
    elif service == 'email':
        recipients = [r.strip() for r in smtp_recv.split(';') if r.strip()]
        return EmailNotifier(smtp_host, smtp_port, smtp_addr, smtp_pwd, recipients)
    else:
        return NoopNotifier()
