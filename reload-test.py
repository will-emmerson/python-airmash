from time import sleep

from reloadr import autoreload


@autoreload
class A:
    def __init__(self):
        while 1:
            print(3)
            sleep(1)


A()
