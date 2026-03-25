from typing import Any, override


from nd_utility.data.storage.interface import Interface as StorageInterface
from nd_utility.oop.design_pattern.structural.decoration.decorator import Decorator as BaseDecorator

class Decorator(BaseDecorator, StorageInterface):
    """
    Base storage decoration that forwards to an inner_composite StorageInterface.
    """

    def __init__(self, inner: StorageInterface):
        """
        .__inner is either the most basic object, in this case group.storage.basic.Yaml or a decoration
        Args:
            inner:
        """
        BaseDecorator.__init__(self, inner)

    @override
    def load(self) -> Any:
        return self._inner.load()

    @override
    def save(self) -> None:
        return self._inner.save()

    @override
    def set_ram(self,content:Any)->None:
        self._inner.set_ram(content)

    @override
    def add_to_ram(self, content:Any) -> None:
        self._inner.set_ram(self._inner.get_ram() + content)

    @override
    def earase(self) -> None:
        self._inner.earase()

    @override
    def earase_ram(self) -> None:
        self._inner.earase_ram()

    @override
    def get_ram(self) -> Any:
        return self._inner.get_ram()
