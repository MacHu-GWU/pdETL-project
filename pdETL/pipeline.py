#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlite4dummy import * 
from collections import deque
from datetime import datetime
import logging
import os

log_dir = "log"
try:
    os.mkdir(log_dir)
except:
    pass

logger = logging.getLogger("pdETL")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

fh = logging.FileHandler(
    os.path.join(
        log_dir, 
        "%s.log" % datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")))
formatter = logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s][%(message)s]")
fh.setFormatter(formatter)
logger.addHandler(fh)

class PipeLine(object):
    def __init__(self, db_file):
        self.engine = Sqlite3Engine(db_file, autocommit=False, echo=False)
        self.queue = deque()
        
    def add_csv(self, csvfile):
        self.queue.append(csvfile)
        
    def flush(self):
        while len(self.queue) >= 1:
            datafile = self.queue.popleft()
            try:
                datafile.metadata.create_all(self.engine)
            except:
                pass

            ins = datafile.table.insert()
            for doc in datafile.generate_rows():
                try:
                    self.engine.insert_row(ins, Row.from_dict(doc))
                except Exception as e:
                    logger.info("%s: %s" % (e.__class__, e))
            self.engine.commit()
            
    def update(self):
        while len(self.queue) >= 1:
            datafile = self.queue.popleft()
            try:
                datafile.metadata.create_all(self.engine)
            except:
                pass

            ins = datafile.table.insert()
            for doc in datafile.generate_rows():
                try:
                    self.engine.insdate_many_row(ins, [Row.from_dict(doc),])
                except Exception as e:
                    logger.info(e)
            self.engine.commit()