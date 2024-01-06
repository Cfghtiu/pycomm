"""序列化和反序列化测试"""
from dataclasses import dataclass

from pycomm import DataStream, Serializable

byte = int


@dataclass
class Color(Serializable):
    r: 'byte'
    g: 'byte'
    b: 'byte'
    a: 'byte' = 255

    """
    # 想再快一点可以直接重写write方法
    def write(self, stream: DataStream):
        # 这样写比用父类方法还慢
        # stream << self.r
        # stream << self.g
        # stream << self.b
        # stream << self.a
        
        # 这样最快
        stream.write(bytes([self.r, self.g, self.b, self.a]))

    @classmethod
    def read(cls, stream: DataStream):
        return Color(*stream.read(4))
    """


class A(Serializable):
    color: Color
    """
    # 这样写也行
    def write(self, stream: DataStream):
        stream << self.color

    @classmethod
    def read(cls, stream: DataStream):
        return A(stream >> Color)
    """

    def __init__(self, color: Color):
        self.color = color

    def __repr__(self):
        return f"A(color={self.color})"


a = A(Color(123, 222, 114))
print(a)  # A(color=Color(r=123, g=222, b=114, a=255))

# 序列化
data = DataStream()
a.write(data)
print(data.getvalue(), list(data.getvalue()))  # b'{\xder\xff' [123, 222, 114, 255]

# 反序列化
data.seek(0)
a2 = A.read(data)
print(a2, a == a2)  # A(color=Color(r=123, g=222, b=114, a=255)) False
