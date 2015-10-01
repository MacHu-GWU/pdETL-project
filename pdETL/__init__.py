#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

from .datatype import DataType
from .csvfile import CSVFile
from .pipeline import PipeLine
from .matchcol import find_mapping

__version__ = "0.0.1"
__short_description__ = ("Batch CSV to sqlite3 ETL tools.")

__all__ = ["DataType", "CSVFile", "PipeLine", "find_mapping"]
