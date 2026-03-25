from typing import Iterable, List, Optional, Tuple, Union

from graphviz import Digraph

from nd_utility.data.kind.group.group import Group
from nd_utility.data.kind.group.kind.UniKind import UniKind as UniKindGroup
from nd_utility.oop.design_pattern.structural.composition.component import Component
from nd_utility.oop.design_pattern.structural.composition.leaf import Leaf


class Composite(Component):

    def __init__(self):
        Component.__init__(self)
        self._children = Group()

    def _would_create_cycle(self, child: Component) -> bool:
        for node in child.walk():
            if node is self:
                return True
        return False

    def _has_direct_child_by_identity(self, child: Component) -> bool:
        for existing_child in self._children:
            if existing_child is child:
                return True
        return False

    def _generate_child_auto_name(self, child: Component) -> str:
        """
        Generates an auto name like Mind_1, Mind_2, Body_1, ...
        This is stored internally for debugging and uniqueness in naming.
        The rendered label is still the class name unless the name was explicitly set.
        """
        base_name = child.__class__.__name__

        count = 0
        for existing_child in self.get_child_group_members():
            if existing_child.__class__.__name__ == base_name:
                count += 1

        return base_name + "_" + str(count + 1)

    def _normalize_child_lookup_name(self, name_or_type: Union[str, type]) -> str:
        if isinstance(name_or_type, str):
            if len(name_or_type.strip()) == 0:
                raise ValueError("name must not be empty.")
            return name_or_type

        if isinstance(name_or_type, type):
            return name_or_type.__name__

        raise TypeError("name_or_type must be a str or a type.")

    def add_child(self, child: Component) -> None:

        if child is self:
            raise ValueError("Cannot add node to itself.")

        if self._would_create_cycle(child):
            raise ValueError("Adding this child would create a cycle.")

        if self._has_direct_child_by_identity(child):
            return

        auto_name = self._generate_child_auto_name(child)
        child.set_auto_name_if_missing(auto_name)
        child.set_parent(self)

        self._children.add_member(child)

    def add_children(self, children: List[Component]) -> None:
        for child in children:
            self.add_child(child)

    def remove_child(self, child: Component) -> None:
        self._children.remove_member(child)
        child.set_parent(None)

    def has_direct_child(self, child: Component) -> bool:
        return self._has_direct_child_by_identity(child)

    def find_children_by_name(self, name_or_type: Union[str, type]) -> List[Tuple[str, Component]]:
        target_name = self._normalize_child_lookup_name(name_or_type)

        found_children: List[Tuple[str, Component]] = []

        for child in self.get_child_group_members():

            if child.has_explicit_name():
                match_name = child.get_name()
            else:
                match_name = child.__class__.__name__

            if match_name == target_name:
                found_children.append((child.get_path(), child))

            if isinstance(child, Composite):
                found_children.extend(child.find_children_by_name(target_name))

        return found_children

    def get_child(self, name_or_type: Union[str, type]) -> Component:
        target_name = self._normalize_child_lookup_name(name_or_type)
        found_children = self.find_children_by_name(target_name)

        if len(found_children) == 0:
            raise ValueError("No child found with name: " + target_name)

        if len(found_children) > 1:
            found_paths = []
            for found_path, found_child in found_children:
                found_paths.append(found_path)

            raise ValueError(
                "Multiple children found with name '" + target_name + "': " + str(found_paths)
            )

        return found_children[0][1]

    def get_child_group_members(self) -> Tuple[Component, ...]:
        return tuple(self._children)

    def get_children(self) -> UniKindGroup[Leaf]:
        return self._children

    def is_leaf(self) -> bool:
        return False

    def get_depth(self) -> int:

        if not self._children:
            return 1

        return 1 + max(current_child.get_depth() for current_child in self._children)

    def get_size(self) -> int:
        return 1 + sum(current_child.get_size() for current_child in self._children)

    def walk(self) -> Iterable[Component]:

        yield self

        for current_child in self._children:
            yield from current_child.walk()

    def stringify(self) -> str:

        lines = [self.get_name()]

        for child in self._children:
            child_lines = child.stringify().splitlines()
            for child_line in child_lines:
                lines.append("  " + child_line)

        return "\n".join(lines)

    def get_tree(self, prefix: str = "", is_last: bool = True) -> str:

        branch = "└── "
        if not is_last:
            branch = "├── "

        lines = [prefix + branch + self.get_name()]

        children = list(self.get_child_group_members())

        for index, child in enumerate(children):

            is_child_last = False
            if index == len(children) - 1:
                is_child_last = True

            new_prefix = prefix
            if is_last:
                new_prefix = new_prefix + "    "
            else:
                new_prefix = new_prefix + "│   "

            lines.append(child.get_tree(new_prefix, is_child_last))

        return "\n".join(lines)

    def get_graphviz(self, dot=None, parent_identifier: Optional[str] = None) -> Digraph:
        dot = Component.get_graphviz(self, dot=dot, parent_identifier=parent_identifier)

        current_node_identifier = self.get_graphviz_node_identifier()

        for child in self.get_child_group_members():
            child.get_graphviz(dot=dot, parent_identifier=current_node_identifier)

        return dot