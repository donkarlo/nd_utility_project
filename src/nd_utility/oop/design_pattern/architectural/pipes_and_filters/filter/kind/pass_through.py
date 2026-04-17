from nd_utility.oop.design_pattern.architectural.pipes_and_filters.filter.filter import Filter


class PassThrough(Filter):
    def process(self, data: object) -> object:
        return data