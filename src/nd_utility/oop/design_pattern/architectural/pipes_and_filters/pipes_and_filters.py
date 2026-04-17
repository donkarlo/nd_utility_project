from typing import List, Type

from nd_utility.oop.design_pattern.architectural.pipes_and_filters.filter.filter import Filter
from nd_utility.oop.design_pattern.architectural.pipes_and_filters.pipe.pipe import Pipe


class PipesAndFilters:
    def __init__(self) -> None:
        self._filter_classes: List[Type[Filter]] = []
        self._filters: List[Filter] = []
        self._source_pipe = Pipe()
        self._sink_pipe = Pipe()
        self._built = False

    def add_filter(self, filter_class: Type[Filter]) -> None:
        if self._built:
            raise RuntimeError("Cannot add a filter after the pipeline has been built.")

        self._filter_classes.append(filter_class)

    def build(self) -> None:
        if self._built:
            raise RuntimeError("The pipeline has already been built.")

        if len(self._filter_classes) == 0:
            raise RuntimeError("At least one filter is required.")

        self._filters = []
        previous_pipe = self._source_pipe

        for filter_index, filter_class in enumerate(self._filter_classes):
            is_last_filter = filter_index == len(self._filter_classes) - 1

            if is_last_filter:
                next_pipe = self._sink_pipe
            else:
                next_pipe = Pipe()

            filter_instance = filter_class(previous_pipe, next_pipe)
            self._filters.append(filter_instance)
            previous_pipe = next_pipe

        self._built = True

    def write(self, data: object) -> None:
        if not self._built:
            raise RuntimeError("Build the pipeline before writing data.")

        self._source_pipe.write(data)

    def run(self) -> object:
        if not self._built:
            raise RuntimeError("Build the pipeline before running it.")

        for current_filter in self._filters:
            current_filter.run()

        return self.read()

    def read(self) -> object:
        if not self._built:
            raise RuntimeError("Build the pipeline before reading data.")

        return self._sink_pipe.read()

    def get_source_pipe(self) -> Pipe:
        return self._source_pipe

    def get_sink_pipe(self) -> Pipe:
        return self._sink_pipe

    def get_filters(self) -> List[Filter]:
        return list(self._filters)