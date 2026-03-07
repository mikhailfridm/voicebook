"""Tests for the dialog state machine."""

import pytest
from app.core.state_machine import StateMachine, SessionContext, State, Intent


@pytest.fixture
def session():
    return SessionContext(call_id="test-001", caller_phone="+79991234567")


@pytest.fixture
def sm(session):
    return StateMachine(session)


class TestHappyPath:
    """Full booking flow: greeting -> service -> master -> slot -> confirm -> name -> booking -> done."""

    def test_full_booking_flow(self, sm, session):
        assert session.state == State.GREETING

        sm.transition(Intent.BOOK)
        assert session.state == State.SERVICE_SELECT

        sm.transition(Intent.SELECT_SERVICE)
        assert session.state == State.MASTER_SELECT

        sm.transition(Intent.SELECT_MASTER)
        assert session.state == State.SLOT_SEARCH

        sm.transition(Intent.SELECT_SLOT)
        assert session.state == State.SLOT_CONFIRM

        sm.transition(Intent.CONFIRM)
        assert session.state == State.CLIENT_INFO

        sm.transition(Intent.PROVIDE_NAME)
        assert session.state == State.BOOKING

        sm.transition(Intent.CONFIRM)
        assert session.state == State.CONFIRM
        assert sm.is_terminal()

    def test_any_master_flow(self, sm, session):
        sm.transition(Intent.BOOK)
        sm.transition(Intent.SELECT_SERVICE)
        sm.transition(Intent.ANY_MASTER)
        assert session.state == State.SLOT_SEARCH

    def test_slot_deny_goes_back(self, sm, session):
        sm.transition(Intent.BOOK)
        sm.transition(Intent.SELECT_SERVICE)
        sm.transition(Intent.SELECT_MASTER)
        sm.transition(Intent.SELECT_SLOT)
        assert session.state == State.SLOT_CONFIRM

        sm.transition(Intent.DENY)
        assert session.state == State.SLOT_SEARCH

    def test_direct_slot_select_skips_confirm(self, sm, session):
        sm.transition(Intent.BOOK)
        sm.transition(Intent.SELECT_SERVICE)
        sm.transition(Intent.SELECT_MASTER)
        sm.transition(Intent.SELECT_SLOT)
        # Client directly selects a time in SLOT_CONFIRM
        sm.transition(Intent.SELECT_SLOT)
        assert session.state == State.CLIENT_INFO


class TestFallback:
    def test_fallback_after_two_unclear(self, sm, session):
        sm.transition(Intent.UNCLEAR)
        assert session.state == State.GREETING
        assert session.misunderstand_count == 1

        sm.transition(Intent.UNCLEAR)
        assert session.state == State.FALLBACK
        assert sm.is_terminal()

    def test_clear_intent_resets_counter(self, sm, session):
        sm.transition(Intent.UNCLEAR)
        assert session.misunderstand_count == 1

        sm.transition(Intent.BOOK)
        assert session.misunderstand_count == 0
        assert session.state == State.SERVICE_SELECT


class TestCancel:
    def test_cancel_from_greeting(self, sm, session):
        sm.transition(Intent.CANCEL)
        assert session.state == State.CLIENT_INFO

    def test_cancel_from_service_select(self, sm, session):
        sm.transition(Intent.BOOK)
        sm.transition(Intent.CANCEL)
        assert session.state == State.CONFIRM

    def test_cancel_from_slot_confirm(self, sm, session):
        sm.transition(Intent.BOOK)
        sm.transition(Intent.SELECT_SERVICE)
        sm.transition(Intent.SELECT_MASTER)
        sm.transition(Intent.SELECT_SLOT)
        sm.transition(Intent.CANCEL)
        assert session.state == State.CONFIRM


class TestQuestion:
    def test_question_stays_in_state(self, sm, session):
        sm.transition(Intent.BOOK)
        assert session.state == State.SERVICE_SELECT

        sm.transition(Intent.QUESTION)
        assert session.state == State.SERVICE_SELECT

    def test_question_does_not_increase_misunderstand(self, sm, session):
        sm.transition(Intent.QUESTION)
        assert session.misunderstand_count == 0


class TestInvalidTransitions:
    def test_unknown_intent_stays(self, sm, session):
        sm.transition(Intent.PROVIDE_NAME)  # invalid from GREETING
        assert session.state == State.GREETING

    def test_terminal_state_no_transition(self, sm, session):
        session.state = State.CONFIRM
        sm.transition(Intent.BOOK)
        assert session.state == State.CONFIRM
