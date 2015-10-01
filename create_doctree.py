#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from docfly import Docfly
import shutil
 
try:
    shutil.rmtree(r"source\pdETL")
except Exception as e:
    print(e)
     
docfly = Docfly("pdETL", dst="source")
docfly.fly()
