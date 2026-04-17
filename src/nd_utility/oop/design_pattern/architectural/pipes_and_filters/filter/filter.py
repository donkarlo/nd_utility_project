from abc import ABC, abstractmethod

from nd_utility.oop.design_pattern.architectural.pipes_and_filters.pipe.pipe import Pipe


class Filter(ABC):
    def __init__(self, input_pipe: Pipe, output_pipe: Pipe) -> None:
        self._input_pipe = input_pipe
        self._output_pipe = output_pipe

    def run(self) -> None:
        input_data = self._input_pipe.read()
        output_data = self.process(input_data)
        self._output_pipe.write(output_data)

    @abstractmethod
    def process(self, data: object) -> object:
        raise NotImplementedError()

    def get_input_pipe(self) -> Pipe:
        return self._input_pipe

    def get_output_pipe(self) -> Pipe:
        return self._output_pipe