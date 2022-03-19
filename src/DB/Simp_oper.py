import attr
import enum


@attr.dataclass(frozen=True)
class SimpOperations:

    @staticmethod
    def less():
        return '$lt'

    @staticmethod
    def more():
        return '$gt'

    @staticmethod
    def equal():
        return 'eq'
