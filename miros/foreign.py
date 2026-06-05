from collections import deque
from typing import Any

from miros.hsm import HsmEventProcessor


class _ForeignBuffers:
    """Typed holder for the spy/trace ring buffers of a foreign HSM."""

    spy: "deque[Any]"   # spy items received over a network; Any is honest here
    trace: "deque[str]"


class ForeignHsm:
    """
    Provides an object that can be filled with the trace/spy information coming
    from another statechart on a different host.
    """

    def __init__(self) -> None:
        self.foreign = _ForeignBuffers()
        self.foreign.spy = deque(maxlen=HsmEventProcessor.SPY_RING_BUFFER_SIZE)
        self.foreign.trace = deque(maxlen=HsmEventProcessor.TRC_RING_BUFFER_SIZE)

    def clear_spy(self) -> None:
        self.foreign.spy.clear()

    def clear_trace(self) -> None:
        self.foreign.trace.clear()

    def trace(self) -> str:
        strace = ""
        for tr in self.foreign.trace:
            strace += tr
            strace += "\n"
        return strace

    def spy(self) -> list[Any]:
        return list(self.foreign.spy)

    def append_to_spy(self, item: Any) -> None:
        self.foreign.spy.append(item)

    def append_to_trace(self, item: str) -> None:
        self.foreign.trace.append(item)
