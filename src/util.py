'''
Created on 30-11-2011

@author: ksuszyns
'''
class Dictionary(dict):
    def __getitem(self, key):
        return dict.__getitem__(self, key)
    
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)
    
    def __setattr__(self, key):
        return dict.__setitem__(self, key)
       
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)

D = Dictionary

class SystemException(RuntimeError):
    pass

class BussinessLogicException(RuntimeError):
    pass
