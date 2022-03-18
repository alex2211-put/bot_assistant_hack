import enum
import attr
@attr.dataclass(frozen=True)
class Simp_oper():
    
    def less():
        return '$lt'
    def more():
        return '$gt'
    def equal():
        return 'eq'



print(Simp_oper.less())