from pycomm.DataStream import DataStream
from typing import Union, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from pycomm.Serializable import Serializable


class Struct:
    def __init__(self, *types: Union[type, str, type['Serializable']]):
        self.write_funcs: list[Callable[[DataStream, object], None]] = []
        self.read_funcs: list[Callable[[DataStream], object]] = []

        from pycomm.Serializable import Serializable
        for type_ in types:
            if isinstance(type_, str):
                name = type_.lower()
                self.write_funcs.append(getattr(DataStream, "write_" + name))
                self.read_funcs.append(getattr(DataStream, "read_" + name))
            elif issubclass(type_, Serializable):
                self.write_funcs.append(lambda data, obj: type_.write(obj, data))
                self.read_funcs.append(type_.read)
            else:
                name = type_.__name__.lower()
                self.write_funcs.append(getattr(DataStream, "write_" + name))
                self.read_funcs.append(getattr(DataStream, "read_" + name))

    def dump(self, *args, stream: DataStream):
        for func, arg in zip(self.write_funcs, args):
            func(stream, arg)

    def load(self, stream: DataStream):
        return [func(stream) for func in self.read_funcs]
