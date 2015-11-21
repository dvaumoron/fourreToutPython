'''
Created on 29 janv. 2015

@author: dvaumoron
'''

import codi

ci = codi.CacheInitializer()
ci.call(0).set(1)
@codi.memoizeWith(ci.cache)
def fact(n):
    return n * fact(n-1)

ci = codi.CacheInitializer()
ci.call(0).set(0)
ci.call(1).set(1)
@codi.memoizeWith(ci.cache)
def fib(n):
    return fib(n - 1) + fib(n - 2)

@codi.memoize
def coef(n, k):
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    else:
        return coef(n - 1, k - 1) + coef(n - 1, k)

if __name__ == '__main__':
    print(fact(10))
    print(fact)
    print(fact.cache)
    print(fib(10))
    print(fib)
    print(fib.cache)
    print(coef(5, 0))
    print(coef(5, 1))
    print(coef(5, 2))
    print(coef(5, 3))
    print(coef(5, 4))
    print(coef(5, 5))
    print(coef)
    print(coef.cache)

    class TestClass:
        __slots__ = "__d"
        def __init__(self):
            self.d = {}
        def __call__(self, a, b=None, *varargs, **keywords):
            print("__call__ of TestClass")
            return self.d
        @property
        def d(self):
            print("d getter of TestClass")
            return self.__d
        @d.setter
        def d(self, d):
            print("d setter of TestClass")
            self.__d = d

    decoratorStr = codi.buildDecorator(TestClass)
    print(decoratorStr)
    exec(decoratorStr)

    class TestClassDecoratorImpl(TestClassDecorator):
        def __init__(self, inner):
            super().__init__(inner)
            self.count = 0
        def __call__(self, a, b=None, *varargs, **keywords):
            self.count += 1
            print("__call__ of TestClassDecoratorImpl", self.count)
            return super().__call__(a, b, *varargs, **keywords)

    compositeStr = codi.buildComposite(TestClass)
    print(compositeStr)
    exec(compositeStr)

    tc = TestClass()
    print(tc)
    d = TestClassDecoratorImpl(tc)
    print(d)
    print(d(1))
    d.d[1] = 1
    print(tc.d)
    print(d.d)
    c = TestClassComposite([])
    c.addInner(tc)
    c.addInner(d)
    print(c)
    c(1)
    c.d = []
    print(c.d)
    print(tc.d)

    @codi.Singleton
    class TestSingleton:
        def __init__(self, name):
            self.name = name
        def __str__(self):
            return self.name

    a = TestSingleton('a')
    b = TestSingleton('b')

    print(a)
    print(b)
    print(TestSingleton.instance)
    print(a == b)
    print(TestSingleton)

    class TestObservable(codi.Observable):
        pass

    class TestObservator:
        def __init__(self, name):
            self.name = name
        def notify(self, observable):
            print(self.name, "notified with", observable)

    observable = TestObservable()
    observator1 = TestObservator("observator1")
    observator2 = TestObservator("observator2")
    observable.registerObservator(observator1)
    observable.registerObservator(observator2)
    observable.registerObservator(observator1)
    observable.notify()
    observable.unregisterObservator(observator2)
    observable.notify()

    @codi.curry
    def myPrint(a, b, c, d, e):
        print(a, b, c, d, e)

    print(myPrint)
    myPrint(1, 2, 3, 5, 7)
    myPrint(1)(2)(3)(5)(7)
    myPrint1 = myPrint(1)
    print(myPrint1)
    myPrint1(2, 3)(5, 7)
    myPrint1(c=3, b=2)(e=7, d=5)
