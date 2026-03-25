from nd_utility.oop.design_pattern.structural.composition.component import Component
from nd_utility.oop.inheritance.overriding.override_from import override_from


class Leaf(Component):
    """Leaf node with no children."""

    def __init__(self):
        Component.__init__(self)

    @override_from(Component)
    def stringify(self) -> str:
        return self.get_name()

    @override_from(Component)
    def get_tree(self, prefix: str = "", is_last: bool = True) -> str:
        return prefix + ("└── " if is_last else "├── ") + self.get_name()