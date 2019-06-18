import weakref

class Deleters:
    def __init__(self):
        self.collection = weakref.WeakKeyDictionary()
    def new(self, identifier):
        d = Deleter()
        self.collection[identifier] = d
        return d
    def remove(self, identifier):
        print(identifier)
        print(list(self.collection.items()))
        # exit()
        try:
            del self.collection[identifier]
        except:
            pass
class Deleter:
    pass
