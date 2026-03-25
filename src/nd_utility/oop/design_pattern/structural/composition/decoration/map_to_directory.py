from pathlib import Path
import re
from typing import Dict, List, Set, Tuple, Union

import numpy as np

from nd_utility.oop.design_pattern.structural.composition.component import Component
from nd_utility.oop.design_pattern.structural.composition.composite import Composite
from nd_utility.oop.design_pattern.structural.composition.decoration.decorator import Decorator


class MapToDirectory(Decorator):

    def __init__(self, inner_composite: Composite, start_directory_path: Union[str, Path], children_directory_name:str, default_file_type:str) -> None:
        if not isinstance(inner_composite, Composite):
            raise TypeError("inner_composite must be an instance of Composite.")

        Decorator.__init__(self, inner_composite)
        self._start_directory_path = Path(start_directory_path).expanduser().resolve()
        self._renamed_file_paths: List[Tuple[Path, Path]] = []
        self._extra_paths_found: List[Path] = []

        self._children_directory_name = children_directory_name
        self._default_file_type = default_file_type

    def operation(self):
        return self._inner.operation()

    def export(self) -> Path:
        self._renamed_file_paths.clear()
        self._extra_paths_found.clear()

        self._start_directory_path.mkdir(parents=True, exist_ok=True)

        root_directory_name = self.__get_export_name(self._inner, ())
        root_directory_path = self._start_directory_path / self.__to_snake_case(root_directory_name)

        root_directory_path.mkdir(parents=True, exist_ok=True)
        self._export_composite(self._inner, root_directory_path)

        self._ask_user_about_renamed_files()
        self._ask_user_about_extra_paths()

        return root_directory_path

    def get_renamed_file_paths(self) -> Tuple[Tuple[Path, Path], ...]:
        return tuple(self._renamed_file_paths)

    def get_extra_paths_found(self) -> Tuple[Path, ...]:
        return tuple(self._extra_paths_found)

    def _export_composite(self, composite: Composite, composite_directory_path: Path) -> None:
        composite_directory_path.mkdir(parents=True, exist_ok=True)

        children_directory_path = composite_directory_path / self._children_directory_name
        children_directory_path.mkdir(parents=True, exist_ok=True)

        children = composite.get_child_group_members()
        expected_names_in_this_level = self.__build_expected_child_entry_names(children)

        self.__collect_extra_paths_in_level(
            children_directory_path=children_directory_path,
            expected_entry_names=expected_names_in_this_level
        )

        for child in children:
            child_export_name = self.__get_export_name(child, children)

            if isinstance(child, Composite):
                child_directory_path = children_directory_path / self.__to_snake_case(child_export_name)
                child_directory_path.mkdir(parents=True, exist_ok=True)
                self._export_composite(child, child_directory_path)
            else:
                self.__export_leaf(
                    leaf=child,
                    parent_children_directory_path=children_directory_path,
                    export_name=child_export_name
                )

    def __export_leaf(self, leaf: Component, parent_children_directory_path: Path, export_name: str) -> None:
        file_name = self.__to_snake_case(export_name) + f".{self._default_file_type}"
        file_path = parent_children_directory_path / file_name

        if file_path.exists():
            backup_file_path = self.__rename_existing_file_to_old(file_path)
            self._renamed_file_paths.append((file_path, backup_file_path))

        np.savez(
            file_path,
            component_name=leaf.get_name(),
            component_class=leaf.__class__.__name__
        )

    def __build_expected_child_entry_names(self, children: Tuple[Component, ...]) -> Set[str]:
        expected_entry_names: Set[str] = set()

        for child in children:
            child_export_name = self.__get_export_name(child, children)
            child_snake_name = self.__to_snake_case(child_export_name)

            if isinstance(child, Composite):
                expected_entry_names.add(child_snake_name)
            else:
                expected_entry_names.add(child_snake_name + f".{self._default_file_type}")

        return expected_entry_names

    def __collect_extra_paths_in_level(self, children_directory_path: Path, expected_entry_names: Set[str]) -> None:
        if not children_directory_path.exists():
            return

        for existing_path in children_directory_path.iterdir():
            if existing_path.name not in expected_entry_names:
                self._extra_paths_found.append(existing_path)

    def __rename_existing_file_to_old(self, file_path: Path) -> Path:
        if not file_path.exists():
            raise FileNotFoundError("file_path does not exist.")
        if not file_path.is_file():
            raise ValueError("file_path must be a file.")

        parent_directory_path = file_path.parent
        file_stem = file_path.stem
        file_suffix = file_path.suffix

        candidate_path = parent_directory_path / ("old_" + file_stem + file_suffix)

        if not candidate_path.exists():
            file_path.rename(candidate_path)
            return candidate_path

        index = 2
        while True:
            candidate_path = parent_directory_path / ("old_" + str(index) + "_" + file_stem + file_suffix)
            if not candidate_path.exists():
                file_path.rename(candidate_path)
                return candidate_path
            index += 1

    def _ask_user_about_renamed_files(self) -> None:
        if len(self._renamed_file_paths) == 0:
            return

        print()
        print("Renamed existing files:")
        print()

        for new_file_path, old_file_path in self._renamed_file_paths:
            print("A previous file was renamed before export.")
            print("New file path: " + str(new_file_path))
            print("Old file backup path: " + str(old_file_path))

            should_delete_old = self.__ask_yes_no(
                prompt="Do you want to delete the old backup file? [y/n]: "
            )

            if should_delete_old:
                old_file_path.unlink()
                print("Deleted: " + str(old_file_path))
            else:
                print("Kept: " + str(old_file_path))

            print()

    def _ask_user_about_extra_paths(self) -> None:
        if len(self._extra_paths_found) == 0:
            return

        print()
        print("Extra filesystem entries found that are not part of the current composite level definitions:")
        print()

        for extra_path in self._extra_paths_found:
            print("Extra path found: " + str(extra_path))

            should_delete_extra = self.__ask_yes_no(
                prompt="Do you want to delete this extra path? [y/n]: "
            )

            if should_delete_extra:
                self.__delete_path(extra_path)
                print("Deleted: " + str(extra_path))
            else:
                print("Kept: " + str(extra_path))

            print()

    def __delete_path(self, path: Path) -> None:
        if not path.exists():
            return

        if path.is_file():
            path.unlink()
            return

        if path.is_dir():
            self.__delete_directory_recursively(path)
            return

        raise ValueError("Unsupported filesystem entry: " + str(path))

    def __delete_directory_recursively(self, directory_path: Path) -> None:
        for child_path in directory_path.iterdir():
            if child_path.is_dir():
                self.__delete_directory_recursively(child_path)
            else:
                child_path.unlink()

        directory_path.rmdir()

    def __ask_yes_no(self, prompt: str) -> bool:
        while True:
            answer = input(prompt).strip().lower()

            if answer == "y":
                return True

            if answer == "n":
                return False

            print("Please answer with 'y' or 'n'.")

    def __get_export_name(self, component: Component, siblings: Tuple[Component, ...]) -> str:
        if component.has_explicit_name():
            return component.get_name()

        current_name = component.get_name()
        class_name = component.__class__.__name__

        pattern = r"^" + re.escape(class_name) + r"_(\d+)$"
        match = re.match(pattern, current_name)

        if match is None:
            return current_name

        same_class_count = 0
        for sibling in siblings:
            if sibling.__class__ is component.__class__:
                same_class_count += 1

        if same_class_count <= 1:
            return class_name

        return current_name

    def __to_snake_case(self, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("value must be a str.")

        normalized_value = value.strip()
        if len(normalized_value) == 0:
            raise ValueError("value must not be empty.")

        normalized_value = normalized_value.replace("-", "_")
        normalized_value = normalized_value.replace(" ", "_")

        normalized_value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized_value)
        normalized_value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", normalized_value)
        normalized_value = re.sub(r"_+", "_", normalized_value)

        return normalized_value.lower()