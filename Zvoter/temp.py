def coro1():
    print("C1: Start")
    print("C1: Stop")


def coro2():
    print("C2: Start")
    print("C2: a")
    print("C2: b")
    print("C2: c")
    print("C2: Stop")


coro1()
coro2()