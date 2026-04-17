from nd_utility.oop.design_pattern.architectural.pipes_and_filters.filter.filter import Filter
from nd_utility.oop.design_pattern.architectural.pipes_and_filters.pipes_and_filters import PipesAndFilters


class TrimFilter(Filter):
    def process(self, data: object) -> object:
        if not isinstance(data, str):
            raise TypeError("TrimFilter expects a string.")

        return data.strip()


class LowercaseFilter(Filter):
    def process(self, data: object) -> object:
        if not isinstance(data, str):
            raise TypeError("LowercaseFilter expects a string.")

        return data.lower()


class ReplaceSpacesWithDashFilter(Filter):
    def process(self, data: object) -> object:
        if not isinstance(data, str):
            raise TypeError("ReplaceSpacesWithDashFilter expects a string.")

        return data.replace(" ", "-")


def main() -> None:
    pipeline = PipesAndFilters()
    pipeline.add_filter(TrimFilter)
    pipeline.add_filter(LowercaseFilter)
    pipeline.add_filter(ReplaceSpacesWithDashFilter)
    pipeline.build()

    pipeline.write("   Hello World From Pipes And Filters   ")
    result = pipeline.run()

    print(result)


if __name__ == "__main__":
    main()