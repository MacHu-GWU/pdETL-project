#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

try:
    from pdETL.timewrapper import timewrapper
except ImportError:
    from timewrapper import timewrapper
except ImportError:
    from .timewrapper import timewrapper

try:
    from pdETL.matchcol import find_mapping
except ImportError:
    from matchcol import find_mapping
except ImportError:
    from .matchcol import find_mapping

try:
    from pdETL.datatype import DataType
except ImportError:
    from datatype import DataType
except ImportError:
    from .datatype import DataType

from sqlite4dummy import *
from sqlite4dummy import dtype as dtype_

from typarse import TypeParser
from collections import OrderedDict
import pandas as pd
import numpy as np
from pprint import pprint as ppt

_parser = TypeParser()
_parser_map = {
    "INTTYPE": _parser.parse_int,
    "FLOATTYPE": _parser.parse_float,
    "TEXTTYPE": _parser.parse_str,
    "DATETYPE": _parser.parse_date,
    "DATETIMETYPE": _parser.parse_datetime,
}
_sqlite4dummy_dtype_map = {
    "INTTYPE": dtype_.INTEGER,
    "FLOATTYPE": dtype_.REAL,
    "TEXTTYPE": dtype_.TEXT,
    "DATETYPE": dtype_.DATE,
    "DATETIMETYPE": dtype_.DATETIME,
}

_SQLITE_CREATE_TABLE_TEMPLATE = \
"""
%s
(
%s%s
)
"""

class CSVFile(object):
    """
    target_schema中的column是CSV文件中原本的列名, 而不是数据库中的列名。
    mapping中的是{CSV中的列名: 数据库中的列名}
    """
    nrows = 10
    
    def __init__(self, table_name, abspath, sep=",", quotechar='"', 
        header=0, usecols=None, iterator=True, chunksize=1000,
        target_schema=dict(), mapping=dict(), primary_keys=[], converter=None):
        # validate input arguments
        self.table_name = table_name
        self.abspath = abspath
        self.sep = sep
        self.quotechar = quotechar
        self.header = header
        self.iterator=iterator
        self.chunksize=chunksize
        self.usecols = usecols
        self.mapping = mapping
        self.primary_keys = primary_keys

        # 检查header, 如果没有, 则自动将header设置为 prefix+column_number
        # 并且将dtype中的column序号也转变成prefix+column_number
        if header == None:
            self.prefix = "c"
            fixed_dtype = OrderedDict()
            for k, v in target_schema.items():
                fixed_dtype[self.prefix + str(k)] = v
            self.target_schema = fixed_dtype
        else:
            self.prefix = None
            self.target_schema = target_schema

        # 根据target_schema中的定义, 解析出pandas.read_csv(dtype=pd_dtype)中输入参数
        # 储存在pd_dtype变量里
        if target_schema:
            pd_dtype = dict()
            for k, v in target_schema.items():
                pd_dtype[k] = v.pd_type
            self.pd_dtype = pd_dtype
        else:
            self.target_schema = dict()
            self.pd_dtype = None
            
        self.analysis_mapping()
        self.construct_sqlite_table()
#         self.create_sqlite_sql()
        
    @staticmethod
    def set_nrows(value):
        if isinstance(value, int):
            CSVFile.nrows = value
        else:
            raise ValueError("CSVFile.set_nrows only takes integer argument.")
    
    @staticmethod
    def set_chunksize(value):
        if isinstance(value, int):
            CSVFile.chunksize = value
        else:
            raise ValueError("CSVFile.set_chunksize only takes integer argument.")

    def analysis_mapping(self):
        """
        """
        for df in pd.read_csv(self.abspath, sep=self.sep, 
            quotechar=self.quotechar, header=self.header,
            dtype=self.pd_dtype, usecols=self.usecols, prefix=self.prefix,
            iterator=True, chunksize=self.chunksize):
            
            columns = list(df.columns)
            
            new_mapping = OrderedDict()
            for before in columns:
                if before not in self.mapping:
                    new_mapping[before] = before
                else:
                    new_mapping[before] = self.mapping[before]
            self.mapping = new_mapping
            
            new_target_schema = OrderedDict()
            for column, dtype in zip(columns, df.dtypes):
                if column not in self.target_schema:
                    new_target_schema[column] = DataType.get_type_by_type(dtype)
                else:
                    new_target_schema[column] = self.target_schema[column]
            self.target_schema = new_target_schema
            break

        for column in self.primary_keys:
            if column not in self.mapping.values():
                raise Exception("Primary Key are not any of the columns")
    
    def construct_sqlite_table(self):
        ### Construct Database.Table Metadata
        columns = list()
        for column_name, dtype in self.target_schema.items():
            new_column_name = self.mapping[column_name]
            
            if new_column_name in self.primary_keys:
                primary_key_flag = True
            else:
                primary_key_flag = False
                
            columns.append(Column(new_column_name, 
                                  _sqlite4dummy_dtype_map[dtype.name], 
                                  primary_key=primary_key_flag))
        
        self.metadata = MetaData()
        self.table = Table(self.table_name, self.metadata, *columns)
    
    def create_sqlite_sql(self):
        # construct CREATE TABLE ... sql
        clause_CREATE_TABLE = "CREATE TABLE %s" % self.table_name
        
        arguments = list()
        for column, dtype in zip(self.mapping.values(), self.target_schema.values()):
            arguments.append("%s %s" % (column, dtype.sqlite_type))
        clause_DATATYPE = "\t" + ",\n\t".join(arguments)
            
        if len(self.primary_keys) == 0:
            clause_PRIMARY_KEY = ""
        else:
            clause_PRIMARY_KEY = ",\n\tPRIMARY KEY (%s)" % ", ".join(self.primary_keys)

        self.create_sql = _SQLITE_CREATE_TABLE_TEMPLATE % (
            clause_CREATE_TABLE, clause_DATATYPE, clause_PRIMARY_KEY,)

        # construct INSERT INTO ... sql
        sql_INSERT_INTO = "INSERT INTO\t%s" % self.table_name
        sql_COLUMNS = "(%s)" % ", ".join(list(self.mapping.values()))
        sql_KEYWORD_VALUES = "VALUES"
        sql_QUESTION_MARK = "(%s)" % ", ".join(["?"] * len(self.target_schema) )
        template = "%s\n\t%s\n%s\n\t%s;"
        self.insert_sql = template % (sql_INSERT_INTO,
                               sql_COLUMNS,
                               sql_KEYWORD_VALUES,
                               sql_QUESTION_MARK,)

    def generate_rows(self):
        """
        """
        for df in pd.read_csv(self.abspath, sep=self.sep, 
            quotechar=self.quotechar, header=self.header,
            dtype=self.pd_dtype, usecols=self.usecols, prefix=self.prefix,
            iterator=True, chunksize=self.chunksize):
            
            # 转换整列的Date或是DateTime
            for column, dtype in self.target_schema.items():
                df[column] = list(map(_parser_map[dtype.name], df[column]))

            for _, series in df.iterrows():
                new_dict = OrderedDict()
                for column, value in series.iteritems():
                    new_dict[self.mapping[column]] = value
                yield new_dict
