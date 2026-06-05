# to test this:
# pytest -s -m thread_safe_attributes
import re
import inspect
from threading import RLock
from typing import Any, NamedTuple


class FrameData(NamedTuple):
    filename: str
    line_number: int
    function_name: str
    # inspect.getframeinfo Traceback.code_context is list[str] | None
    lines: list[str] | None
    # named frame_index (not "index") to avoid shadowing tuple.index()
    frame_index: int | None


class ThreadSafeAttribute:
    def __init__(self, initial_value: Any = None) -> None:
        self._initial_value: Any = initial_value
        self._is_atomic: bool = True
        self._lock: RLock = RLock()
        self._value: Any = initial_value

    def is_not_atomic(self, previous_line: str) -> bool:
        is_not_atomic = True
        # search for '+=', '-=' ... '<<=', '**='
        is_not_atomic &= (
            re.search(r"([+-/*@^&|<>%]=)|([/<>*]{2}=)", previous_line) is not None
        )
        return is_not_atomic

    def request_for_lock(self, previous_line: str) -> bool:
        request_for_lock = False
        # search for _, _lock = ...
        if "_lock" in previous_line:
            request_for_lock |= re.search(r"_, _lock[ ]+=", previous_line) is not None
        return request_for_lock

    def __get__(self, instance: object, owner: type | None = None) -> Any:
        # Return type is Any: this descriptor conditionally returns either the
        # stored value or a (value, lock) tuple when the caller requests a lock.
        # A union return would require callers to downcast on every access, which
        # is not the intended API.  Any is honest here.
        self._lock.acquire(blocking=True)
        self._is_atomic = True
        current_frame = inspect.currentframe()
        assert current_frame is not None  # always called from within a frame
        previous_frame = current_frame.f_back
        assert previous_frame is not None  # always has a caller frame
        fdata = FrameData(*inspect.getframeinfo(previous_frame))
        assert fdata.lines is not None  # context=1 (default) always yields a list
        previous_line = fdata.lines[0]
        if self.is_not_atomic(previous_line):
            # print('{} not atomic'.format(fdata.lines[0]))
            self._is_atomic = False
        else:
            # print('{} is atomic'.format(fdata.lines[0]))
            # print("get releasing lock")
            self._lock.release()
        if self.request_for_lock(previous_line):
            # print("providing lock")
            return self._value, self._lock
        else:
            return self._value

    def __set__(self, instance: object, value: Any) -> None:
        if self._is_atomic:
            # print("set aquiring lock")
            self._lock.acquire(blocking=True)
        else:
            # print("set continuing non atomic operation")
            pass
        self._value = value
        self._is_atomic = True
        # print("set releasing lock")
        self._lock.release()


class MetaThreadSafeAttributes(type):
    def __init__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        /,
        **kwargs: Any,
    ) -> None:
        """Build thread safe attributes"""
        # _attributes is an optional class-level list defined by user subclasses;
        # getattr is load-bearing here: the metaclass genuinely introspects an
        # attribute it does not own, with no typed alternative.
        attributes = getattr(cls, "_attributes", None)
        if attributes is not None:
            for name in list(set(attributes)):
                setattr(cls, name, ThreadSafeAttribute(initial_value=0))
        super().__init__(name, bases, namespace, **kwargs)
