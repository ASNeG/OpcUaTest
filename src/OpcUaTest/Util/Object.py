from sympy.logic.boolalg import false
class Object(dict):
    
    def __init__(self, *args, **kwargs):
        super(Object, self).__init__()
        
        # Set property attributes
        self.__dict__["Property"] = {
            "AddMissingItem": True
        }
        for key in kwargs:
            self.__dict__["Property"][key] = kwargs[key]
       
        # Set data
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict) and type(v).__name__ != "Object":
                        self.__dict__[k] = Object(v, **self.__dict__["Property"])
                    else:
                        self.__dict__[k] = v
 
            
    def size(self):
        return len(self.__dict__) -  1
    
    
    def deleteEmptyItems(self):
        for k in list(self.__dict__):
            v = self.__dict__[k]
            if type(v).__name__ != "Object": continue
            v.deleteEmptyItems()
            
            if v.size() == 0:
                del self.__dict__[k]
    
    def keys(self):
        keys = []
        for key in self.__dict__:
            if key == "Property": continue
            keys.append(key)
        return keys
    
    
    def get(self, path):
        if type(path).__name__ == "str":
            return self.get(path.split('.'))
            
        if type(path).__name__ != "list":
            return None
        
        if len(path) == 1:
            if path[0] not in self.__dict__: return None
            return self.__dict__[path[0]]   
        else:
            key = path.pop(0)
            if key not in self.__dict__: return None
            if type(self.__dict__[key]).__name__ != "Object": return None
            return self.__dict__[key].get(path)
        
        
    def exist(self, path):
        if type(path).__name__ == "str":
            return self.exist(path.split('.'))
            
        if type(path).__name__ != "list":
            return False
        
        if len(path) == 1:
            if path[0] not in self.__dict__: return False
            return path[0] in self.__dict__
        else:
            key = path.pop(0)
            if key not in self.__dict__: return False
            if type(self.__dict__[key]).__name__ != "Object": return False
            return self.__dict__[key].exist(path)        
    

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        if isinstance(value, dict) and type(value).__name__ != "Object":
            self.__dict__.update({key: Object(value, **self.__dict__["Property"])})
        else:
            self.__dict__.update({key: value})
            
 
    def __getattr__(self, attr):
        return self[attr]

            
    def __getitem__(self, key):
        if key not in self.__dict__ and self.__dict__["Property"]["AddMissingItem"] == True:
            self.__dict__.update({key: Object({}, **self.__dict__["Property"])})
        return self.__dict__[key]
            

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        del self.__dict__[key]
   
        
    def __str__(self):
        rawStr = "{"
        for key in self.__dict__:
            if key == "Property": continue
            if len(rawStr) > 1: rawStr += ", "
            rawStr = rawStr + "'" + key + "' : "
            if isinstance(self.__dict__.get(key), dict):
                rawStr = rawStr + str(self.__dict__.get(key))
            else:
                rawStr = rawStr + str(self.__dict__.get(key))
        rawStr += "}"
            
        return rawStr