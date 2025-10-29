#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Authentication Handler for Udemy API

Manages authentication credentials and generates auth headers for API requests.
Supports session-based authentication via cookies and credentials from .env file.
"""

import os
import sys
import json
from pathlib import Path
from getpass import getpass


class Authenticator:
    """
    Handles Udemy authentication and generates request headers.

    Supports multiple authentication methods:
    1. Credentials from .env file
    2. Interactive prompts
    3. Cookie/token extraction (future enhancement)
    """

    def __init__(self, project_root):
        """
        Initialize authenticator.

        Args:
            project_root: Path to project root directory (where .env is located)
        """
        self.project_root = Path(project_root)
        self.env_file = self.project_root / '.env'
        self.cookies_file = self.project_root / 'cookies.json'
        self.credentials = {}
        self.cookies = {}

        # Load cookies first, then credentials (cookies can work without credentials)
        self._load_cookies()
        self._load_credentials()

    def _load_credentials(self):
        """Load credentials from .env file or prompt user."""
        # Try to load from .env first
        if self.env_file.exists():
            self._read_env_file()

        # Validate credentials and prompt if missing (only if no cookies available)
        # If we have session cookies, credentials are optional
        if not self._has_valid_credentials() and not self.cookies:
            print("⚠️  Credentials not found or incomplete in .env file")
            self._prompt_for_credentials()

    def _read_env_file(self):
        """Read and parse .env file."""
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue

                    # Parse KEY=VALUE format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]

                        self.credentials[key] = value

        except Exception as e:
            print(f"⚠️  Error reading .env file: {e}")

    def _load_cookies(self):
        """
        Load session cookies from cookies.json file.

        The cookies.json file should contain cookies from an authenticated browser session.
        Format: Array of cookie objects or simple key-value dict.

        Example formats supported:
        1. Simple dict: {"access_token": "...", "client_id": "..."}
        2. Cookie array: [{"name": "access_token", "value": "..."}, ...]
        """
        if not self.cookies_file.exists():
            return

        try:
            with open(self.cookies_file, 'r') as f:
                data = json.load(f)

            if isinstance(data, dict):
                # Simple key-value format
                self.cookies = data
            elif isinstance(data, list):
                # Cookie object array format (from browser dev tools or Playwright)
                for cookie in data:
                    if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                        self.cookies[cookie['name']] = cookie['value']

            if self.cookies:
                print(f"  ✓ Loaded {len(self.cookies)} cookies from cookies.json")

        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON in cookies.json: {e}")
        except Exception as e:
            print(f"⚠️  Error reading cookies.json: {e}")

    def _has_valid_credentials(self):
        """Check if we have minimum required credentials."""
        username = self.credentials.get('UDEMY_USERNAME', '').strip()
        password = self.credentials.get('UDEMY_PASSWORD', '').strip()

        # Check for placeholder values from .env.example
        if username and password:
            if 'example.com' not in username and 'password-here' not in password:
                return True

        return False

    def _prompt_for_credentials(self):
        """Interactively prompt user for credentials."""
        print("\n🔐 Please enter your Udemy credentials:")
        print("(These will be used for this session only. Update .env to save them.)\n")

        try:
            username = input("Udemy Email: ").strip()
            password = getpass("Udemy Password: ").strip()

            if username and password:
                self.credentials['UDEMY_USERNAME'] = username
                self.credentials['UDEMY_PASSWORD'] = password
                print()
            else:
                raise ValueError("Username and password cannot be empty")

        except KeyboardInterrupt:
            print("\n\n⚠️  Authentication cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Error getting credentials: {e}")
            sys.exit(1)

    def get_auth_headers(self):
        """
        Get authentication headers for API requests.

        Returns:
            dict: Headers to include in API requests

        Note:
            Uses session-based authentication via cookies.
            Cookies should be provided in cookies.json file.
        """
        # Basic headers structure based on research findings
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Referer': self.credentials.get('UDEMY_URL', 'https://www.udemy.com'),
        }

        # Add session cookies if available
        if self.cookies:
            # Build Cookie header from cookies dict
            cookie_parts = []
            for name, value in self.cookies.items():
                cookie_parts.append(f"{name}={value}")
            headers['Cookie'] = '; '.join(cookie_parts)

        # Store credentials for later use if needed
        if self._has_valid_credentials():
            self._username = self.credentials.get('UDEMY_USERNAME')
            self._password = self.credentials.get('UDEMY_PASSWORD')

        return headers

    def get_credentials(self):
        """
        Get raw credentials for authentication flows.

        Returns:
            dict: Credentials with 'username' and 'password' keys
        """
        if not self._has_valid_credentials():
            raise ValueError("No valid credentials available")

        return {
            'username': self.credentials.get('UDEMY_USERNAME'),
            'password': self.credentials.get('UDEMY_PASSWORD'),
            'url': self.credentials.get('UDEMY_URL', '')
        }

    def get_session_cookies(self):
        """
        Get session cookies loaded from cookies.json.

        Returns:
            dict: Cookie key-value pairs
        """
        return self.cookies

    def has_session_cookies(self):
        """
        Check if session cookies are available.

        Returns:
            bool: True if cookies are loaded
        """
        return len(self.cookies) > 0


# Example usage
if __name__ == '__main__':
    # Test authentication
    # Use current working directory as base (works for both local and Git-installed plugins)
    project_root = Path.cwd() / 'udemy-research'

    try:
        auth = Authenticator(project_root)
        headers = auth.get_auth_headers()

        print("✓ Authentication successful!")
        print(f"\nHeaders generated:")
        for key, value in headers.items():
            # Don't print full auth values for security
            if 'auth' in key.lower() or 'token' in key.lower():
                print(f"  {key}: [REDACTED]")
            else:
                print(f"  {key}: {value[:50]}..." if len(value) > 50 else f"  {key}: {value}")

    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        sys.exit(1)
