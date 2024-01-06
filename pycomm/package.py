import inspect

from pycomm.Struct import Struct
from functools import cache


class Package:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        self.parameters = [para.annotation for para in inspect.signature(func).parameters.values()]
        self.package_handler = None
        self.__get__ = cache(self.__get__)

    def __call__(self, *args):
        """用于 A.b(instance, *args)，或者a(*args)，如果是后者，就用不了remote_call函数，因为没有PackageSender"""
        if args and isinstance(args[0], PackageSender):
            self.__get__(args[0], args[0].__class__)(*args[1:])
            return
        self.func(*args)

    def handler(self, handler) -> "Package":
        """设置包的处理器"""
        self.package_handler = handler
        return self

    def __get__(self, instance, owner) -> "BoundPackage":
        return BoundPackage(instance, self)


class BoundPackage:
    """绑定某个类的包"""
    def __init__(self, instance: "PackageSender", package: Package):
        self.package = package
        self.instance = instance
        self.parameters = self.package.parameters.copy()
        self.parameters.pop(0)  # 删掉self
        self.struct = Struct(*self.parameters)

    def __call__(self, *args):
        """用于 a.b(*args)"""
        global _args, _instance, _package
        _instance = self.instance
        _args = args
        _package = self
        self.package.func(self, *args)

    def name(self) -> str:
        return self.package.name

    def handle(self, *args):
        self.package.package_handler(self.instance, *args)

    def enable(self):
        self.instance.enabled_packages[self.package.name] = self

    def disable(self):
        self.instance.enabled_packages.pop(self.package.name, None)


class PackageSender:
    def __init__(self):
        self.enabled_packages: dict[str, BoundPackage] = {}

    def send_package(self, bound_package: BoundPackage, *args):
        """发送数据包方法"""


_args: tuple
_instance: PackageSender
_package: "BoundPackage"


def remote_call(*args):
    args = args or _args
    _instance.send_package(_package, *args)
