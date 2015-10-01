from pdETL import *
import unittest
import os

class CSVFileUnittest(unittest.TestCase):
    def test_generate_row_01(self):
        _dir = r"testdata\workspace1"
        for basename in os.listdir(_dir):
            abspath = os.path.join(_dir, basename)
            csvfile = CSVFile("advertisement", abspath, 
                target_schema={"id": DataType.text, "hour": DataType.datetime})
            for row in csvfile.generate_rows():
                print(row)
                 
    def test_generate_row_02(self):
        _dir = r"testdata\workspace2"
        for basename in os.listdir(_dir):
            abspath = os.path.join(_dir, basename)
            csvfile = CSVFile("employee", abspath, 
                target_schema={"employee_id": DataType.text, "start_date": DataType.date})
            for row in csvfile.generate_rows():
                print(row)
 
    def test_generate_row_03(self):
        _dir = r"testdata\workspace3"
        for basename in os.listdir(_dir):
            abspath = os.path.join(_dir, basename)
            csvfile = CSVFile("employee_id", abspath, header=None, 
                target_schema={0: DataType.text, 2: DataType.date})
            for row in csvfile.generate_rows():
                print(row)
            
    def test_generate_row_04(self):
        _dir = r"testdata\workspace4"
        for basename in os.listdir(_dir):
            abspath = os.path.join(_dir, basename)
            csvfile = CSVFile("data", abspath, header=0, 
                target_schema={"_id": DataType.text, "_int": DataType.integer, 
                               "_float": DataType.float, "_str": DataType.text})
            for row in csvfile.generate_rows():
                print(row)            
    
if __name__ == "__main__":
    unittest.main()
    
