#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pdETL import *
import unittest

class PipeLineUnittest(unittest.TestCase):
    def test_flush(self):
        pipeline = PipeLine(":memory:")
        
        csvfile = CSVFile(
            "data",
            r"testdata\workspace4\data.txt",
            sep=",",
            header=0,
            target_schema={"_id": DataType.text, "_int": DataType.integer, 
                           "_float": DataType.float, "_str": DataType.text},
            mapping={"_id": "id", "_int": "int", "_float": "float", "_str": "str"},
            primary_keys=["id"],
        )
        
        pipeline.add_csv(csvfile)
        pipeline.add_csv(csvfile)
        pipeline.flush()
        
        pipeline.engine.prt_all(csvfile.table)
    
    def test_update(self):
        pipeline = PipeLine(":memory:")
        
        csvfile = CSVFile(
            "data",
            r"testdata\workspace4\data.txt",
            sep=",",
            header=0,
            target_schema={"_id": DataType.text, "_int": DataType.integer, 
                           "_float": DataType.float, "_str": DataType.text},
            mapping={"_id": "id", "_int": "int", "_float": "float", "_str": "str"},
            primary_keys=["id"],
        )
        
        pipeline.add_csv(csvfile)
        pipeline.add_csv(csvfile)
        pipeline.update()
        
        pipeline.engine.prt_all(csvfile.table)
        
if __name__ == "__main__":
    unittest.main()