#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
column name fuzzy match.
"""

try:
    from pdETL.packages.fuzzywuzzy.process import extractOne
except ImportError:
    from packages.fuzzywuzzy.process import extractOne
except ImportError:
    from .packages.fuzzywuzzy.process import extractOne
    
def find_mapping(before, after, mapping=dict()):
    """
    
    :param before:
    :param after:
    :param mapping:
    
    **中文文档**
    
    为每一个after中的字符串, 从before中挑选出能匹配上的成员。如果在 ``mapping``
    中预先被定义了, 则使用预定义的映射。
    
    注意: before和after必须都要是没有重复的字符串列表。
    
    但after的数量可以多于before。因为有的时候, 我们持续地将数据从before导入到
    after, 其中before的一列可能被copy了两份导入到after中的两列中。而我们导入了
    一批数据后, 可能对after中的某一列做一定修改, 然后继续导入下一批数据。所以
    after的数量多于before是存在应用场景的。
    """
    if (len(set(before)) != len(before)) or (len(set(after)) != len(after)):
        raise Exception("Duplicate column name found!")
    
    for k, v in mapping.items():
        if (k not in after) or (v not in before):
            raise Exception("Invalid Mapping: %s" % mapping)
    
    for target in after:
        if target not in mapping:
            mapping[target] = extractOne(target, before)[0]
            
    return mapping

    
if __name__ == "__main__":
    import unittest
    
    class MatchUnittest(unittest.TestCase):
        def test_1(self):
            before = ["_id", "_int", "_float", "_str"]
            after = ["id", "int", "float", "str"]
            expect_ = {
                "id": "_id", "int": "_int", "float": "_float", "str": "_str"}
            result_ = find_mapping(before, after)
            self.assertDictEqual(result_, expect_)

        def test_2(self):
            before = ["_id", "_int", "_float", "_str"]
            after = ["id", "int", "float", "str", "stringnumber"]
            expect_ = {
                "id": "_id", "int": "_int", "float": "_float", "str": "_str", "stringnumber": "_int"}
            result_ = find_mapping(before, after, mapping={"stringnumber": "_int"})
            self.assertDictEqual(result_, expect_)

    unittest.main()