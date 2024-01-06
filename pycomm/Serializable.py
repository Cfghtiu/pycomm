from pycomm.DataStream import DataStream
from pycomm.Struct import Struct


class Serializable:
    def __init_subclass__(cls, fill=True):
        if fill:
            cls.struct = Struct(*cls.__annotations__.values())

    @classmethod
    def read(cls, stream: DataStream):
        return cls(*cls.struct.load(stream))

    def write(self, stream: DataStream):
        for key, write_func in zip(self.__annotations__.keys(), self.struct.write_funcs):
            write_func(stream, getattr(self, key))
