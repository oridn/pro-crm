class Foo(object):
    _instance = None

    def __init__(self,name):
        self.name = name

    @classmethod
    def instance(cls,*args,**kwargs):
        if not Foo._instance:
            obj = Foo(*args,**kwargs)
            Foo._instance = obj
        return Foo._instance


obj1 = Foo.instance('alex')
obj2 = Foo.instance('alex')
print(id(obj1),id(obj2))