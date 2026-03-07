"""
State Machine for VoiceBook dialog flow.

States:
  GREETING -> SERVICE_SELECT -> MASTER_SELECT -> SLOT_SEARCH ->
  SLOT_CONFIRM -> CLIENT_INFO -> BOOKING -> CONFIRM

  Any state can transition to FALLBACK on repeated misunderstanding.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class State(str, Enum):
    GREETING = "greeting"
    SERVICE_SELECT = "service_select"
    MASTER_SELECT = "master_select"
    SLOT_SEARCH = "slot_search"
    SLOT_CONFIRM = "slot_confirm"
    CLIENT_INFO = "client_info"
    BOOKING = "booking"
    CONFIRM = "confirm"
    FALLBACK = "fallback"


class Intent(str, Enum):
    BOOK = "book"
    CANCEL = "cancel"
    QUESTION = "question"
    SELECT_SERVICE = "select_service"
    SELECT_MASTER = "select_master"
    ANY_MASTER = "any_master"
    SELECT_SLOT = "select_slot"
    PROVIDE_NAME = "provide_name"
    CONFIRM = "confirm"
    DENY = "deny"
    DENY_SLOT = "deny_slot"
    RESCHEDULE = "reschedule"
    UNCLEAR = "unclear"


@dataclass
class SessionContext:
    """Holds all data collected during the call."""
    call_id: str
    caller_phone: str = ""
    state: State = State.GREETING

    # Collected data
    service_id: Optional[int] = None
    service_name: Optional[str] = None
    master_id: Optional[int] = None
    master_name: Optional[str] = None
    slot_datetime: Optional[str] = None
    client_name: Optional[str] = None
    booking_id: Optional[int] = None

    # Client info from CRM lookup
    client_info: Optional[dict] = None

    # Available options (populated from API)
    available_slots: list = field(default_factory=list)

    # Fallback counter
    misunderstand_count: int = 0
    max_misunderstand: int = 2

    # Conversation history for LLM
    messages: list = field(default_factory=list)


# Allowed transitions: current_state -> {intent: next_state}
TRANSITIONS: dict[State, dict[Intent, State]] = {
    State.GREETING: {
        Intent.BOOK: State.SERVICE_SELECT,
        Intent.CANCEL: State.CLIENT_INFO,
        Intent.RESCHEDULE: State.CLIENT_INFO,
        Intent.QUESTION: State.GREETING,
    },
    State.SERVICE_SELECT: {
        Intent.SELECT_SERVICE: State.MASTER_SELECT,
        Intent.CANCEL: State.CONFIRM,
        Intent.QUESTION: State.SERVICE_SELECT,
    },
    State.MASTER_SELECT: {
        Intent.SELECT_MASTER: State.SLOT_SEARCH,
        Intent.ANY_MASTER: State.SLOT_SEARCH,
        Intent.CANCEL: State.CONFIRM,
        Intent.QUESTION: State.MASTER_SELECT,
    },
    State.SLOT_SEARCH: {
        Intent.SELECT_SLOT: State.SLOT_CONFIRM,
        Intent.DENY_SLOT: State.SLOT_SEARCH,
        Intent.CANCEL: State.CONFIRM,
        Intent.QUESTION: State.SLOT_SEARCH,
    },
    State.SLOT_CONFIRM: {
        Intent.CONFIRM: State.CLIENT_INFO,
        Intent.DENY: State.SLOT_SEARCH,
        Intent.DENY_SLOT: State.SLOT_SEARCH,
        Intent.SELECT_SLOT: State.CLIENT_INFO,
        Intent.CANCEL: State.CONFIRM,
        Intent.QUESTION: State.SLOT_CONFIRM,
    },
    State.CLIENT_INFO: {
        Intent.PROVIDE_NAME: State.BOOKING,
        Intent.CANCEL: State.CONFIRM,
        Intent.QUESTION: State.CLIENT_INFO,
    },
    State.BOOKING: {
        Intent.CONFIRM: State.CONFIRM,
        Intent.CANCEL: State.CONFIRM,
        Intent.QUESTION: State.BOOKING,
    },
    State.CONFIRM: {},  # terminal
    State.FALLBACK: {},  # terminal — hand off to human
}


class StateMachine:
    def __init__(self, session: SessionContext):
        self.session = session

    def transition(self, intent: Intent) -> State:
        """Attempt state transition based on intent. Returns new state."""
        current = self.session.state

        if intent == Intent.UNCLEAR:
            self.session.misunderstand_count += 1
            if self.session.misunderstand_count >= self.session.max_misunderstand:
                self.session.state = State.FALLBACK
                logger.info(f"[{self.session.call_id}] FALLBACK after {self.session.max_misunderstand} unclear intents")
                return State.FALLBACK
            return current  # stay, agent will re-ask

        # Reset misunderstand counter on valid intent
        self.session.misunderstand_count = 0

        allowed = TRANSITIONS.get(current, {})
        next_state = allowed.get(intent)

        if next_state is None:
            logger.warning(
                f"[{self.session.call_id}] No transition from {current} with intent {intent}"
            )
            return current

        self.session.state = next_state
        logger.info(f"[{self.session.call_id}] {current} -> {next_state} (intent={intent})")
        return next_state

    def is_terminal(self) -> bool:
        return self.session.state in (State.CONFIRM, State.FALLBACK)
