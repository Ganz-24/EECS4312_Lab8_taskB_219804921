import pytest

from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound


def test_register_until_capacity_then_waitlist_fifo_positions():
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")
    s4 = er.register("u4")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("registered")
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3", "u4"]


def test_cancel_registered_promotes_earliest_waitlisted_fifo():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist

    er.cancel("u1")  # should promote u2

    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == ["u3"]


def test_duplicate_register_raises_for_registered_and_waitlisted():
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

    er.register("u2")  # waitlisted
    with pytest.raises(DuplicateRequest):
        er.register("u2")


def test_waitlisted_cancel_removes_and_updates_positions():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u2")    # remove from waitlist

    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]


def test_capacity_zero_all_waitlisted_and_promotion_never_happens():
    er = EventRegistration(capacity=0)
    assert er.register("u1") == UserStatus("waitlisted", 1)
    assert er.register("u2") == UserStatus("waitlisted", 2)

    # No one can ever be registered when capacity=0
    assert er.status("u1") == UserStatus("waitlisted", 1)
    assert er.status("u2") == UserStatus("waitlisted", 2)
    assert er.snapshot()["registered"] == []

    # Cancel unknown should raise NotFound
    with pytest.raises(NotFound):
        er.cancel("missing")



#################################################################################
# Add your own additional tests here to cover more cases and edge cases as needed.
#################################################################################

def test_reregister_after_cancel():
    """Edge case: user cancels then registers again."""
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.cancel("u1")

    status = er.register("u1")

    assert status == UserStatus("registered")
    assert er.snapshot()["registered"] == ["u1"]


def test_multiple_cancellations_with_multiple_promotions():
    """Edge case: sequential cancellations causing multiple promotions."""
    er = EventRegistration(capacity=2)

    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.register("u4")

    er.cancel("u1")
    er.cancel("u2")

    snap = er.snapshot()

    assert snap["registered"] == ["u3", "u4"]
    assert snap["waitlist"] == []


def test_status_for_absent_user():
    """Edge case: querying status of unknown user."""
    er = EventRegistration(capacity=2)

    er.register("u1")

    assert er.status("unknown") == UserStatus("none")


def test_waitlist_position_after_multiple_changes():
    """Edge case: ensure waitlist positions remain contiguous."""
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.register("u4")

    er.cancel("u3")

    assert er.status("u2") == UserStatus("waitlisted", 1)
    assert er.status("u4") == UserStatus("waitlisted", 2)


def test_constructor_negative_capacity():
    """Edge case: invalid capacity."""
    with pytest.raises(ValueError):
        EventRegistration(-1)

#### Lab 9 Test cases

# Covers C1, C5, AC1, EC6
def test_promotion_when_registered_user_cancels():
    system = EventRegistration(1)

    system.register("u1")
    system.register("u2")
    system.register("u3")

    system.cancel("u1")

    snapshot = system.snapshot()

    assert snapshot["registered"] == ["u2"]
    assert snapshot["waitlist"] == ["u3"]


# Covers C2, AC2
def test_waitlist_fifo_order_preserved():
    system = EventRegistration(2)

    system.register("u1")
    system.register("u2")

    system.register("u3")
    system.register("u4")

    snapshot = system.snapshot()

    assert snapshot["waitlist"] == ["u3", "u4"]


# Covers C3, AC3
def test_status_registered_waitlisted_none():
    system = EventRegistration(1)

    system.register("u1")
    system.register("u2")

    assert system.status("u1") == UserStatus("registered")
    assert system.status("u2") == UserStatus("waitlisted", 1)
    assert system.status("u9") == UserStatus("none")


# Covers C4, AC4
def test_deterministic_snapshot_with_identical_operations():
    system1 = EventRegistration(2)
    system2 = EventRegistration(2)

    operations = ["u1", "u2", "u3", "u4"]

    for user in operations:
        system1.register(user)
        system2.register(user)

    system1.cancel("u1")
    system2.cancel("u1")

    assert system1.snapshot() == system2.snapshot()


# Covers C7, AC6, EC4
def test_cancel_missing_user_raises_notfound():
    system = EventRegistration(2)

    system.register("u1")

    with pytest.raises(NotFound):
        system.cancel("u9")


# Covers C8, C9, AC7, EC5
def test_waitlist_reindex_after_middle_cancellation():
    system = EventRegistration(1)

    system.register("u1")
    system.register("u2")
    system.register("u3")
    system.register("u4")

    system.cancel("u3")

    assert system.status("u2") == UserStatus("waitlisted", 1)
    assert system.status("u4") == UserStatus("waitlisted", 2)


# Covers C6, AC5, EC2
def test_duplicate_registration_when_already_registered():
    system = EventRegistration(2)

    system.register("u1")

    with pytest.raises(DuplicateRequest):
        system.register("u1")


# Covers C6, EC3
def test_duplicate_registration_when_already_waitlisted():
    system = EventRegistration(1)

    system.register("u1")
    system.register("u2")

    with pytest.raises(DuplicateRequest):
        system.register("u2")


# Covers AC8, EC1
def test_capacity_zero_all_users_waitlisted():
    system = EventRegistration(0)

    system.register("u1")
    system.register("u2")

    snapshot = system.snapshot()

    assert snapshot["registered"] == []
    assert snapshot["waitlist"] == ["u1", "u2"]
