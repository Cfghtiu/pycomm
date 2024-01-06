import struct
import sys
import io
from uuid import UUID


class DataStream(io.BytesIO):
    def __init__(self, *args):  # 这段代码删掉后某地方可能会有警告
        super().__init__(*args)

    def __lshift__(self, other):
        if hasattr(other, "write"):
            other.write(self)
        else:
            getattr(self, "write_"+type(other).__name__.lower())(other)
        return self

    def __rshift__(self, other):
        if hasattr(other, "read"):
            return other.read(self)
        if isinstance(other, str):
            return getattr(self, "read_" + other.lower())()
        return getattr(self, "read_" + other.__name__.lower())()

    write_bytes = io.BytesIO.write
    read_bytes = io.BytesIO.read

    def write_int(self, value: int):
        self.write(value.to_bytes(4, sys.byteorder))

    def read_int(self) -> int:
        return int.from_bytes(self.read(4), sys.byteorder)

    def write_short(self, value: int):
        self.write(value.to_bytes(2, sys.byteorder))

    def read_short(self) -> int:
        return int.from_bytes(self.read(2), sys.byteorder)

    def write_str(self, value: str):
        data = value.encode("utf8")
        self.write_short(len(data))
        self.write(data)

    def read_str(self) -> str:
        size = self.read_short()
        data = self.read(size)
        return data.decode("utf8")

    def write_float(self, value: float):
        if sys.byteorder == "little":
            self.write(struct.pack("<f", value))
        else:
            self.write(struct.pack(">f", value))

    def read_float(self) -> float:
        if sys.byteorder == "little":
            return struct.unpack("<f", self.read(4))[0]
        else:
            return struct.unpack(">f", self.read(4))[0]

    def write_long(self, value: int):
        self.write(value.to_bytes(8, sys.byteorder))

    def read_long(self) -> int:
        return int.from_bytes(self.read(8), sys.byteorder)

    def write_double(self, value: float):
        if sys.byteorder == "little":
            self.write(struct.pack("<d", value))
        else:
            self.write(struct.pack(">d", value))

    def read_double(self) -> float:
        if sys.byteorder == "little":
            return struct.unpack("<d", self.read(8))[0]
        else:
            return struct.unpack(">d", self.read(8))[0]

    def write_bool(self, value: bool):
        self.write(value.to_bytes(1, sys.byteorder))

    def read_bool(self) -> bool:
        return bool.from_bytes(self.read(1), sys.byteorder)

    def write_byte(self, value: int):
        self.write(value.to_bytes(1, sys.byteorder))

    def read_byte(self) -> int:
        return int.from_bytes(self.read(1), sys.byteorder)

    def write_uuid(self, value: UUID):
        self.write(value.bytes)

    def read_uuid(self) -> UUID:
        return UUID(bytes=self.read(16))
