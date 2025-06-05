from typing import Any, Generic, Type, TypeVar

T = TypeVar("T")


# type hint so that x = SingletonDecorator(klass) is typed as an instance of klass
class SingletonDecorator(Generic[T]):
    def __init__(self, klass: Type[T]) -> None:
        self.klass = klass
        self.instance: T | None = None

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        if self.instance is None:
            self.instance = self.klass(*args, **kwargs)
        return self.instance
