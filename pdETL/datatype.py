#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
在CSV文件中, 我们只支持四类雯

1. TEXT, unicode, str, np.str
2. INTEGER, int, 
3. FLOAT, float, 
"""

from __future__ import print_function
from datetime import datetime, date
import numpy as np
import sys

if sys.version_info[0] == 3:
    _str_type = str
    _int_types = (int,)
else:
    _str_type = basestring
    _int_types = (int, long)
    
class BASETYPE(object):
    """DataType Base Class.
    """
    def __init__(self):
        self.name = self.__class__.__name__
                
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return "{0}()".format(self.name)
    
class INTTYPE(BASETYPE):
    """Integer type.
    """
    pd_type = np.int64
    instance = (int, np.int, np.int64)
    sqlite_type = "INTEGER"
    
class FLOATTYPE(BASETYPE):
    """Float type.
    """
    pd_type = np.float
    instance = np.float
    sqlite_type = "REAL"
    
class TEXTTYPE(BASETYPE):
    """String type.
    """
    pd_type = np.str
    instance = np.str
    sqlite_type = "TEXT"
    
class DATETYPE(BASETYPE):
    """Date type.
    """
    pd_type = np.str
    instance = (date, np.str)
    sqlite_type = "DATE"
    
class DATETIMETYPE(BASETYPE):
    """Datetime type.
    """
    pd_type = np.str
    instance = (datetime, np.str)
    sqlite_type = "TIMESTAMP"
    
class DATATYPE(object):
    """A DataType container class.
    
    you can access instance of all :class:`BASETYPE` by::
    
        >>> from pdETL.datatype import DataType
        
        >>> DataType.integer
        INTTYPE
        
        >>> DataType.float
        FLOATTYPE
        
        >>> DataType.text
        TEXTTYPE
        
        >>> DataType.date
        DATETYPE
        
        >>> DataType.datetime
        DATETIMETYPE
    """
    def __init__(self):
        self.integer = INTTYPE()
        self.float = FLOATTYPE()
        self.text = TEXTTYPE()
        self.date = DATETYPE()
        self.datetime = DATETIMETYPE()
    
    def get_type_by_instance(self, instance):
        """Get a :class:`BASETYPE` instance by any support datatype instance.
        """
        if isinstance(instance, (int, np.int, np.int32, np.int64)):
            return self.integer
        elif isinstance(instance, (float, np.float, np.float32, np.float64)):
            return self.float
        elif isinstance(instance, (_str_type, np.str, np.object)):
            return self.text
        elif isinstance(instance, date):
            return self.date
        elif isinstance(instance, datetime):
            return self.datetime
        else:
            raise TypeError("Unable to detect type of '%s'" % repr(instance))
    
    def get_type_by_type(self, a_type):
        if a_type in [int, np.int, np.int32, np.int64]:
            return self.integer
        
        elif a_type in [float, np.float, np.float32, np.float64]:
            return self.float
        
        elif a_type in [_str_type, np.str, np.object]:
            return self.text

        elif a_type is date:
            return self.date
        
        elif a_type is datetime:
            return self.datetime

DataType = DATATYPE()

if __name__ == "__main__":
    import unittest
    
    class DataTypeUnittest(unittest.TestCase):
        def test_all(self):
            totest = [INTTYPE(), FLOATTYPE(), TEXTTYPE(), 
                      DATETYPE(), DATETIMETYPE()]
            
            print(totest)
            for i in totest:
                print(i)
            
    unittest.main()
    