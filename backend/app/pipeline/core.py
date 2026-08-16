from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol


class PipelineStep[InputValue, OutputValue](Protocol):
    def run(self, value: InputValue) -> OutputValue: ...


@dataclass(frozen=True)
class Pipeline[InputValue, OutputValue]:
    """A typed synchronous pipeline assembled from small steps."""

    _runner: Callable[[InputValue], OutputValue]

    @staticmethod
    def start[FirstInput, FirstOutput](
        step: PipelineStep[FirstInput, FirstOutput],
    ) -> "Pipeline[FirstInput, FirstOutput]":
        return Pipeline(step.run)

    def then[NextOutput](
        self,
        step: PipelineStep[OutputValue, NextOutput],
    ) -> "Pipeline[InputValue, NextOutput]":
        def run(value: InputValue) -> NextOutput:
            return step.run(self.run(value))

        return Pipeline(run)

    def run(self, value: InputValue) -> OutputValue:
        return self._runner(value)
