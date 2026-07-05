from abc import ABC, abstractmethod

from context import Context


class BaseState(ABC):
    def __init__(self) -> None:
        self.next_state: BaseState | None = None

    def then(self, next_state: "BaseState") -> "BaseState":
        current_next = self.next_state
        if current_next is None:
            self.next_state = next_state
        else:
            current_next.then(next_state)
        return self

    def go_next(self, ctx: Context) -> None:
        if self.next_state is None:
            raise RuntimeError(f"{type(self).__name__} next_state is not set")
        BaseState.transition(ctx, self.next_state)

    @staticmethod
    def transition(ctx: Context, next_state: "BaseState") -> None:
        ctx.next_state = next_state

    @abstractmethod
    def update(self, ctx: Context) -> None:
        pass