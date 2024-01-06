"""一个简单的客户端和服务端的的连接类"""

from pycomm import (
    in_client,
    in_server,
    remote_call,
    PackageSender,
    DataStream,
    BoundPackage
)


class Connection(PackageSender):
    def __init__(self,):
        super().__init__()
        self.data = None

    def send_package(self, bound_package: BoundPackage, *args):
        stream = DataStream()
        stream << bound_package.name()

        # 数据可以一个一个写入
        for arg in args:
            if isinstance(arg, bool):  # 一个一个写入的好处是可以中途修改数据
                arg = not arg
            stream << arg
        # 也可以这样，速度比第一种快，毕竟没用<<(但第一个好看)
        # for write_func, arg in zip(bound_package.struct.write_funcs, args):
        #     if isinstance(arg, bool):
        #         arg = not arg
        #     write_func(stream, arg)

        # 不需要修改数据时也可以直接这样，这样最快
        # bound_package.struct.dump(*args, stream=stream)

        # 发送数据
        self.data = stream.getvalue()

    def recv_data(self):
        """接收数据并处理"""
        data = self.data  # 接收数据
        stream = DataStream(data)

        # 获取包包名，如果没有就代表没有启用或者未知的数据包
        pkg_name = stream >> str
        bound_package = self.enabled_packages.get(pkg_name, None)
        if bound_package is None:
            raise Exception("package not enabled")

        # 和send_package一样可以一个一个读取，方便中途修改数据
        args = []
        for para in bound_package.parameters:
            arg = stream >> para
            if isinstance(arg, bool):
                arg = not arg
            args.append(arg)
        # args = bound_package.struct.load(stream)  # 也可以直接这样
        bound_package.handle(*args)  # 处理包，调用包的处理器

    @in_client
    def login(self, name: str, password: str):
        """客户端发送登录请求"""
        password = password + "233"
        remote_call(name, password)  # =self.send_package(self.login, name, password)

    @login.handler
    def handle_login(self, name: str, password: str):
        """处理登录请求"""
        print(f"login {name} {password}")

    @in_server
    def login_reply(self, result: bool):
        """服务端回复"""
        remote_call()  # =self.send_package(self.login_reply, result)

    @login_reply.handler
    def handle_login_reply(self, result: bool):
        print(f"login reply {result}")


conn = Connection()
conn.login.enable()  # 启用登录包
conn.login_reply.enable()  # 启用登录回复包

# 客户端登录
conn.login("张三", "张三生日")
conn.recv_data()  # 处理登录 print("login 张三 张三生日233")

# 服务端登录回复
conn.login_reply(True)
conn.recv_data()  # 处理登录回复 print("login reply True")
