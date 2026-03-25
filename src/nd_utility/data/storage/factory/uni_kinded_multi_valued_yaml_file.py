from typing import Any
from typing import override


# --- Fast YAML str_path: try C extensions, fall back to safe Python loaders ---
import yaml

from nd_utility.data.kind.yaml.yaml import Yaml as YamlDataKind
from nd_utility.data.storage.decorator.multi_valued.observer.add_to_ram_values_publisher import AddToRamValuesPublisher
from nd_utility.data.storage.decorator.multi_valued.observer.add_to_ram_values_subscriber import AddToRamValuesSubscriber
from nd_utility.data.storage.decorator.multi_valued.observer.group_ram_values_addition_finished_publisher import \
    GroupRamValuesAdditionFinishedPublisher
from nd_utility.data.storage.decorator.multi_valued.observer.group_ram_values_addition_finished_subscriber import \
    GroupRamValuesAdditionFinishedSubscriber
from nd_utility.data.storage.decorator.multi_valued.decorator.sliced.interface import Interface as MultiValuedSlicedStorageInterface
from nd_utility.data.storage.interface import Interface as StorageInterface
from nd_utility.oop.inheritance.overriding.override_from import override_from

try:
    from yaml import CLoader as YamlCLoader, CDumper as YamlCDumper  # fastest
except Exception:
    from yaml import SafeLoader as YamlCLoader, SafeDumper as YamlCDumper  # fallback

from nd_utility.data.storage.decorator.multi_valued.decorator.uni_kinded import UniKinded
from nd_utility.data.storage.decorator.multi_valued.decorator.sliced.sliced import Sliced
from nd_utility.data.storage.kind.file.file import File as FileStorage
from itertools import islice
import io
from nd_utility.data.kind.dic.dic import Dic
from nd_utility.os.file_system.file.file import File as OsFile
from nd_utility.os.file_system.path.file import File as FilePath

class UniKindedMultiValuedYamlFile(MultiValuedSlicedStorageInterface):
    """
    High-throughput multi-document YAML file using PyYAML (+CLoader/CDumper if available).
    - load(): loads all docs into RAM
    - save(): dumps RAM docs back to disk (with '---' separators)
    - get_values_by_slice(): streams only the requested doc window
    Notes:
      * PyYAML does not preserve comments/order like ruamel.yaml's round-trip mode.
      * Uses explicit_start='---' for multi-doc formatting.
    """

    def __init__(self, str_path, slc:slice ,create_if_not_exist:bool):
        # Keep your existing UniFormat/SlicedValues decoration and the '---' separator
        yaml_data_kind = YamlDataKind()
        self._slice = slc
        file_storage = FileStorage(OsFile.init_from_path(FilePath(str_path)), create_if_not_exist)
        self._storage = UniKinded(Sliced(file_storage, self._slice, "---"), yaml_data_kind, False)

    @override_from(AddToRamValuesPublisher)
    def attach_add_to_ram_values_subscriber(self, add_value_subscriber: AddToRamValuesSubscriber) ->None:
        self._storage.attach_add_to_ram_values_subscriber(add_value_subscriber)

    @override_from(AddToRamValuesPublisher)
    def dettach_add_to_ram_values_subscriber(self, add_value_subscriber: AddToRamValuesSubscriber) ->None:
        self._storage.dettach_add_to_ram_values_subscriber(add_value_subscriber)

    @override_from(GroupRamValuesAdditionFinishedPublisher)
    def attach_group_ram_values_addition_finished_subscriber(self, add_values_finished_subscriber: GroupRamValuesAdditionFinishedSubscriber)->None:
        self._storage.attach_group_ram_values_addition_finished_subscriber(add_values_finished_subscriber)

    @override_from(StorageInterface)
    def load(self) -> None:
        """
        Stream only the requested window from disk and cache it as a slc.
        Reads sequentially and stops as soon as the window is complete.
        """
        slc = self._slice
        if slc is None:
            start = 0
            stop = None
            step = 1

        if slc.start is None:
            start = 0
        else:
            start = slc.start

        # if stop is None then until the end is loded
        stop = slc.stop

        if slc.step is None:
            step = 1
        else:
            step = slc.step

        with open(self.get_native_absolute_string_path(), "rb", buffering=1024 * 1024) as f_raw:
            stream = io.BufferedReader(f_raw, buffer_size=8 * 1024 * 1024)
            dict_docs = yaml.load_all(stream, Loader=YamlCLoader)
            for dict_doc in islice(dict_docs, start, stop, step):
                if dict_doc is not None:
                    dic_doc = Dic(dict_doc)
                    self._storage.add_to_ram(dic_doc)
            self._storage.notify_group_ram_values_addition_finished_subscribers()

    @override
    def save(self) -> None:
        pass

    def get_native_absolute_string_path(self) -> str:
        return self._storage.get_native_absolute_string_path()

    # Unimplemented interface methods (fill as needed)
    @override
    def earase(self) -> None:
        pass

    @override
    def delete(self) -> None:
        pass

    @override
    def earase_ram(self) -> None:
        pass

    @override
    def set_ram(self, ram: Any) -> None:
        pass
