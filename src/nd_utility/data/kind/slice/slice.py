class Slice:
    def __init__(self, slc:slice):
        self._slice = slc

    def get_name(self) -> str:
        return f"_sliced_from_{self._slice.start}_to_{self._slice.stop}"