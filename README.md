# pycomm
一个包含发包和序列化工具的库
## 序列化工具用法
```
from pycomm import Struct, DataStream
struct = Struct(str, int, str)
stream = DataStream()
struct.dump("hello", 8, "aaa", stream=stream)

stream2 = DataStream(stream.getvalue())
print(struct.load(stream2))  # ['hello', 8, 'aaa']
```
## 序列化类用法
先创建一个继承Serializable的类
```
from dataclasses import dataclass
from pycomm import Serializable
byte = int
@dataclass
class Color(Serializable):
    r: 'byte'
    g: 'byte'
    b: 'byte'
    a: 'byte' = 255
```
然后进行序列化
```
from pycomm import DataStream
color = Color(1, 2, 3)
stream = DataStream()
stream << color
print(stream.getvalue())  # b'\x01\x02\x03\xff'
```
反序列化方法
```
stream = DataStream(b'\x01\x02\x03\xff')
color = stream >> Color
print(color)
```
## 发包工具用法
```
from pycomm import Package, DataStream
@Package
def say(name: str, msg: str):
    print(f"{name}: {msg}")
stream = DataStream()
say.struct.dump('K', 'Hi', stream=stream)

stream2 = DataStream(stream.getvalue())
say(*say.struct.load(stream2))  # K: Hi
```
## 高级点的发包工具用法
使用自定义类发包，先定义一个类
```
from pycomm import (
    Package,
    DataStream,
    PackageSender,
    BoundPackage,
    remote_call
)
class PkgSender(PackageSender):
    def send_package(self, bound_package: BoundPackage, *args):
        stream = DataStream()
        stream << bound_package.name()
        bound_package.struct.dump(*args, stream=stream)
        print(stream.getvalue())
    @Package
    def say(self, name: str, msg: str):
        remote_call()
    @say.handler
    def say_handler(self, name: str, msg: str):
        print(f"{name}: {msg}")
```
然后创建一个实例并调用say方法
```
p = PkgSender()
p.say("K", "Hi")  # b'\x03\x00say\x01\x00K\x02\x00Hi'
```
如果你要解析数据，那么它那么应该这样处理
```
p.say.enable()  # 启用包
stream = DataStream(b'\x03\x00say\x01\x00K\x02\x00Hi')
name = stream >> str
package = p.enabled_packages[name]
args = package.struct.load(stream)
package.handle(*args)
```
### 更多

更多内容可以看项目中的test1.py和test2.py，它们分别是序列化测试和发包测试
