## Student Name: Matthew Magagna
## Student ID: 219804921

from dataclasses import dataclass
from typing import List, Optional


class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass


class NotFound(Exception):
    """Raised if a user cannot be found for cancellation."""
    pass


@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "none"
    position: 1-based waitlist position if waitlisted; otherwise None
    """
    state: str
    position: Optional[int] = None


class EventRegistration:
    """
    Deterministic event registration system with FIFO waitlist.
    """

    def __init__(self, capacity: int) -> None:
        """
        Args:
            capacity: maximum number of registered users (>= 0)
        """
        if capacity < 0:
            raise ValueError("capacity must be >= 0")

        self.capacity = capacity
        self.registered: List[str] = []
        self.waitlist: List[str] = []

    def register(self, user_id: str) -> UserStatus:
        """
        Register a user.

        - If capacity available -> user is registered.
        - If capacity full or capacity == 0 -> user added to FIFO waitlist.

        Raises:
            DuplicateRequest if user already exists in system.
        """

        # Duplicate detection (FR5, C6)
        if user_id in self.registered or user_id in self.waitlist:
            raise DuplicateRequest()

        # Capacity zero OR full → waitlist
        if self.capacity == 0 or len(self.registered) >= self.capacity:
            self.waitlist.append(user_id)
            return UserStatus("waitlisted", len(self.waitlist))

        # Register directly
        self.registered.append(user_id)
        return UserStatus("registered")

    def cancel(self, user_id: str) -> None:
        """
        Cancel a user.

        - Registered users are removed and the earliest waitlisted user
          is promoted if capacity allows.
        - Waitlisted users are removed and waitlist positions shift.
        - If user not found → NotFound exception.
        """

        # Registered cancellation
        if user_id in self.registered:
            self.registered.remove(user_id)

            # Promote earliest waitlisted user if capacity available
            if self.waitlist and len(self.registered) < self.capacity:
                promoted = self.waitlist.pop(0)
                # Promotion appended to preserve registered order (FR15)
                self.registered.append(promoted)

            return

        # Waitlist cancellation
        if user_id in self.waitlist:
            self.waitlist.remove(user_id)
            # Python list removal automatically preserves order
            # Status queries recompute contiguous 1-based positions (C8, C9)
            return

        # User absent
        raise NotFound()

    def status(self, user_id: str) -> UserStatus:
        """
        Return user status.

        Returns:
            UserStatus("registered")
            UserStatus("waitlisted", position)
            UserStatus("none")
        """

        if user_id in self.registered:
            return UserStatus("registered")

        if user_id in self.waitlist:
            position = self.waitlist.index(user_id) + 1
            return UserStatus("waitlisted", position)

        return UserStatus("none")

    def snapshot(self) -> dict:
        """
        Deterministic snapshot of system state.
        """

        return {
            "registered": list(self.registered),
            "waitlist": list(self.waitlist),
        }
