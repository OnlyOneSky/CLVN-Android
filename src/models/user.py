"""User data model for test data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class User:
    """Immutable representation of a test user.

    Attributes
    ----------
    username:
        Login username / email.
    password:
        Login password.
    expected_name:
        The display name expected after a successful login.
    """

    username: str
    password: str
    expected_name: str = ""
