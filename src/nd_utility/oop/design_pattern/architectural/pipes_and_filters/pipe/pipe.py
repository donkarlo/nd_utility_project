from typing import List

from nd_utility.oop.design_pattern.architectural.pipes_and_filters.pipe.empty_error import EmptyError


class Pipe:
    def __init__(self) -> None:
        self._items: List[object] = []

    def write(self, data: object) -> None:
        self._items.append(data)

    def read(self) -> object:
        if self.is_empty():
            raise EmptyError("Cannot read from an empty pipe.")

        first_item = self._items[0]
        del self._items[0]
        return first_item

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def size(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()
