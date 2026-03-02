"""Message bus module for decoupled channel-agent communication."""

from orbitclaw.bus.events import InboundMessage, OutboundMessage
from orbitclaw.bus.queue import MessageBus

__all__ = ["MessageBus", "InboundMessage", "OutboundMessage"]
