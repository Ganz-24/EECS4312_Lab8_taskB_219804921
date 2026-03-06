## Student Name: Matthew Magagna
## Student ID: 219804921

"""
Task B: Event Registration with Waitlist (Stub)
In this lab, you will design and implement an Event Registration with Waitlist system using an LLM assistant as your primary programming collaborator. 
You are asked to implement a Python module that manages registration for a single event with a fixed capacity. 
The system must:
•	Accept a fixed capacity.
•	Register users until capacity is reached.
•	Place additional users into a FIFO waitlist.
•	Automatically promote the earliest waitlisted user when a registered user cancels.
•	Prevent duplicate registrations.
•	Allow users to query their current status.

The system must ensure that:
•	The number of registered users never exceeds capacity.
•	Waitlist ordering preserves FIFO behavior.
•	Promotions occur deterministically under identical operation sequences.

The module must preserve the following invariants:
•	A user may not appear more than once in the system.
•	A user may not simultaneously exist in multiple states.
•	The system state must remain consistent after every operation.

The system must correctly handle non-trivial scenarios such as:
•	Multiple cancellations in sequence.
•	Users attempting to re-register after canceling.
•	Waitlisted users canceling before promotion.
•	Capacity equal to zero.
•	Simultaneous or rapid consecutive operations.
•	Queries during state transitions.

The output consists of the updated registration state and ordered lists of registered and waitlisted users after each operation.
"""

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
    Event registration system with deterministic ordering.
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
        Register a user:
          - if capacity available -> registered
          - else -> waitlisted (FIFO)

        Raises:
            DuplicateRequest if user already exists
        """

        if user_id in self.registered or user_id in self.waitlist:
            raise DuplicateRequest()

        # Capacity zero means nobody can be registered
        if self.capacity == 0 or len(self.registered) >= self.capacity:
            self.waitlist.append(user_id)
            return UserStatus("waitlisted", len(self.waitlist))

        self.registered.append(user_id)
        return UserStatus("registered")

    def cancel(self, user_id: str) -> None:
        """
        Cancel a user:
          - if registered -> remove and promote earliest waitlisted user
          - if waitlisted -> remove from waitlist
          - if absent -> raise NotFound
        """

        # Registered cancellation
        if user_id in self.registered:
            self.registered.remove(user_id)

            # Promote earliest waitlisted user if capacity allows
            if self.waitlist and len(self.registered) < self.capacity:
                promoted = self.waitlist.pop(0)
                self.registered.append(promoted)

            return

        # Waitlisted cancellation
        if user_id in self.waitlist:
            self.waitlist.remove(user_id)
            return

        raise NotFound()

    def status(self, user_id: str) -> UserStatus:
        """
        Return status of a user:
          - registered
          - waitlisted with position
          - none
        """

        if user_id in self.registered:
            return UserStatus("registered")

        if user_id in self.waitlist:
            position = self.waitlist.index(user_id) + 1
            return UserStatus("waitlisted", position)

        return UserStatus("none")

    def snapshot(self) -> dict:
        """
        Return deterministic snapshot of internal state.
        """

        return {
            "registered": list(self.registered),
            "waitlist": list(self.waitlist),
        }