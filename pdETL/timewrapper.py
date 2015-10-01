#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provide syntactic sugar and useful functions which standard 
datetime and dateutil doesn't have.


Highlight
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- :meth:`TimeWrapper.parse_date()<TimeWrapper.parse_date>`
    a powerful universal date parser
    
- :meth:`TimeWrapper.parse_datetime()<TimeWrapper.parse_datetime>`
    a powerful universal datetime parser
    
- :meth:`TimeWrapper.dtime_range(start, end, freq)<TimeWrapper.dtime_range>
    a datetime series generator
            
- :meth:`TimeWrapper.randdate(start, end)<TimeWrapper.randdate>`
    random date generator
    
- :meth:`TimeWrapper.randdatetime(start, end)<TimeWrapper.randdatetime>`
    random datetime generator
            
- :meth:`TimeWrapper.day_interval()<TimeWrapper.day_interval>`
- :meth:`TimeWrapper.month_interval()<TimeWrapper.month_interval>`
- :meth:`TimeWrapper.year_interval()<TimeWrapper.year_interval>`
    generate day, month, year interval start, end datetime string for 
    SQL ``SELECT * FROM column BETWEEN start_datetime AND end_datetime;`` query.



Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Python2: Yes
- Python3: Yes


Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- None


Class, method, function, exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import print_function
from datetime import datetime, date, timedelta
import random
import sys

is_py2 = (sys.version_info[0] == 2)
if is_py2:
    range = xrange

_DATE_TEMPLATE = {
    "%Y-%m-%d":     "2014-09-20",
    "%m-%d-%Y":     "09-20-2014",
    "%m/%d/%Y":     "09/20/2014",
    "%Y/%m/%d":     "2014/09/20",
    "%B %d, %Y":    "September 20, 2014",
    "%b %d, %Y":    "Sep 20, 2014",
    "%Y%m%d":       "20140920",
    }

_DATETIME_TEMPLATE = {
    "%Y-%m-%d %H:%M:%S":        "2014-01-15 17:58:31",
    "%Y-%m-%d %H:%M:%S.%f":     "2014-01-15 17:58:31.1234",
    "%Y-%m-%d %H:%M":           "2014-01-15 17:58",
    "%Y-%m-%d %I:%M:%S %p":     "2014-01-15 5:58:31 PM",
     
    "%m-%d-%Y %H:%M:%S":        "1-15-2014 17:58:31",
    "%m-%d-%Y %H:%M:%S.%f":     "1-15-2014 17:58:31.1234",
    "%m-%d-%Y %H:%M":           "1-15-2014 17:58",
    "%m-%d-%Y %I:%M:%S %p":     "1-15-2014 5:58:31 PM",
    
    "%m/%d/%Y %H:%M:%S":        "1/15/2014 17:58:31",
    "%m/%d/%Y %H:%M:%S.%f":     "1/15/2014 17:58:31.1234",
    "%m/%d/%Y %H:%M":           "1/15/2014 17:58",
    "%m/%d/%Y %I:%M:%S %p":     "1/15/2014 5:58:31 PM",
    "%m/%d/%Y %I:%M %p":        "1/15/2014 05:58 PM",
    "%m/%d/%Y %I %p":           "1/15/2014 05 PM",
    
    "%Y-%m-%dT%H:%M:%S":        "2014-01-15T17:58:31",
    "%Y-%m-%dT%H:%M:%S.%f":     "2014-01-15T17:58:31.1234",
    
    "%y%m%d%H":                 "14011506",
    }

for pattern, example in _DATE_TEMPLATE.items():
    _DATETIME_TEMPLATE[pattern] = example

##############
# Exceptions #
##############

class ModeError(Exception):
    """Used in TimeWrapper.day_interval, TimeWrapper.month_interval, 
    TimeWrapper.year_interval. For wrong mode argument.
    """
    def __init__(self, mode_name):
        self.mode_name = mode_name

    def __str__(self):
        return ("mode has to be 'str' or 'datetime', default 'str'. "
                "You are using '%s'.") % self.mode_name

class NoMatchingTemplateError(Exception):
    """Used in TimeWrapper.str2date, TimeWrapper.str2datetime. Raised when no
    template matched the string we want to parse.
    """
    def __init__(self, pattern):
        self.pattern = pattern
        
    def __str__(self):
        return "None template matching '%s'" % self.pattern

class TimeWrapper(object):
    """A time related utility class.
    
    **中文文档**
    
    "时间包装器"提供了对时间, 日期相关的许多计算操作的函数。能智能的从各种其他
    格式的时间中解析出Python datetime.datetime/datetime.date 对象。更多功能请
    参考API文档。
    """
    def __init__(self):
        self.date_templates = list(_DATE_TEMPLATE.keys())
        self.datetime_templates = list(_DATETIME_TEMPLATE.keys())

        self.default_date_template = "%Y-%m-%d"               # 日期默认模板
        self.std_dateformat = "%Y-%m-%d"                      # 简单标准模板
        self.default_datetime_templates = "%Y-%m-%d %H:%M:%S" # 日期时间默认模板
        self.std_datetimeformat = "%Y-%m-%d %H:%M:%S"         # 简单标准模板
    
    def add_date_template(self, template):
        """Manually add a date format template so TimeWrapper can recognize it.
        
        A better way is to edit the ``_DATETIME_TEMPLATE`` in source code.
        """
        self.date_templates.append(template)
        
    def add_datetime_template(self, template):
        """Manually add a datetime format template.
        
        A better way is to edit the ``_DATE_TEMPLATE`` and add it.
        """
        self.datetime_templates.append(template)
    
    ##########
    # Parser #
    ##########
    def reformat(self, dtstring, before, after):
        """Edit the time string format.
        
        See https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
        for all format string options.
        
        **中文文档**
        
        将datetime string从一种格式转换成另一种格式。
        """
        a_datetime = datetime.strptime(dtstring, before)
        return datetime.strftime(a_datetime, after)
    
    def str2date(self, datestr):
        """Try parse date from string. If None template matching this datestr, 
        raise Error.
         
        :param datestr: a string represent a date
        :type datestr: str
        :return: a datetime.date object
        
        Usage::
        
            >>> from weatherlab.lib.timelib.timewrapper import timewrapper
            >>> timewrapper.str2date("12/15/2014")
            datetime.date(2014, 12, 15)
        
        **中文文档**
        
        尝试从字符串中解析出datetime.date对象。每次解析时, 先尝试默认模板, 如果
        失败了, 再重新对所有模板进行尝试; 一旦尝试成功, 这将当前成功的模板保存
        为默认模板。这样使得尝试的策略最优化。
        """
        try:
            return datetime.strptime(
                    datestr, self.default_date_template).date()
        except: # 如果默认的模板不匹配, 则重新尝试所有的模板
            pass
        
        # try all date_templates
        # 对每个template进行尝试, 如果都不成功, 抛出异常
        for template in self.date_templates: 
            try:
                a_datetime = datetime.strptime(datestr, template) # 如果成功了
                self.default_date_template = template # 保存为default
                return a_datetime.date()
            except:
                pass
        raise NoMatchingTemplateError(datestr)

    def str2datetime(self, datetimestr):
        """Try parse datetime from string. If None template matching this 
        datestr, raise Error.
         
        :param datetimestr: a string represent a datetime
        :type datetimestr: str
        :return: a datetime.datetime object
        
        Usage::
        
            >>> from weatherlab.lib.timelib.timewrapper import timewrapper
            >>> timewrapper.str2date("12/15/2014 06:30:00 PM")
            datetime.datetime(2014, 12, 15, 18, 30)
    
        **中文文档**
        
        尝试从字符串中解析出datetime.date对象。每次解析时, 先尝试默认模板, 如果
        失败了, 再重新对所有模板进行尝试; 一旦尝试成功, 这将当前成功的模板保存
        为默认模板。这样使得尝试的策略最优化。
        """
        try:
            return datetime.strptime(
                    datetimestr, self.default_datetime_templates)
        except: # 如果默认的模板不匹配, 则重新尝试所有的模板
            pass
        
        # try all datetime_templates
        # 对每个template进行尝试, 如果都不成功, 抛出异常
        for template in self.datetime_templates:
            try:
                a_datetime = datetime.strptime(
                                datetimestr, template) # 如果成功了
                self.default_datetime_templates = template # 保存为default
                return a_datetime
            except:
                pass
        raise NoMatchingTemplateError(datetimestr)
    
    def std_datestr(self, datestr):
        """Reformat a date string to standard format.
        """
        return date.strftime(
                self.str2date(datestr), self.std_dateformat)

    def std_datetimestr(self, datetimestr):
        """Reformat a datetime string to standard format.
        """
        return datetime.strftime(
                self.str2datetime(datetimestr), self.std_datetimeformat)

    ##########################################
    # timestamp, toordinary method extension #
    ##########################################
    def toordinal(self, date_object):
        """Calculate number of days from 0000-00-00.
        """
        return date_object.toordinal()
    
    def fromordinal(self, days):
        """Create a date object that number ``days`` of days after 0000-00-00.
        """
        return date.fromordinal(days)

    def totimestamp(self, datetime_object):
        """Calculate number of seconds from unix timestamp start point 
        "1969-12-31 20:00:00"
        
        Because in python2, datetime module doesn't have timestamp() method,
        so we have to implement in a python2,3 compatible way.
        """
        return (datetime_object - datetime(1969, 12, 31, 20, 0)).total_seconds()
    
    def fromtimestamp(self, timestamp):
        """Create a datetime object that number ``timestamp`` of seconds after 
        unix timestamp start point "1969-12-31 20:00:00".
        
        Because python doesn't support negative timestamp to datetime
        so we have to implement my own method.
        """
        if timestamp >= 0:
            return datetime.fromtimestamp(timestamp)
        else:
            return datetime(1969, 12, 31, 20, 0) + timedelta(seconds=timestamp)

    def parse_date(self, value):
        """A lazy method to parse anything to date.
        
        Usage::
        
            >>> from weatherlab.lib.timelib.timewrapper import timewrapper
            >>> from datetime import datetime
            >>> timewrapper.parse_date("12/25/1985")
            datetime.date(1985, 12, 25)
            >>> timewrapper.parse_date(725000)
            datetime.date(1985, 12, 25)
            >>> timewrapper.parse_date(datetime(1985, 12, 25, 8, 30))
            datetime.date(1985, 12, 25)
        """
        if isinstance(value, str):
            return self.str2date(value)
        elif isinstance(value, int):
            return date.fromordinal(value)
        elif isinstance(value, datetime):
            return value.date()
        else:
            raise Exception("Unable to parse date from: %s, type<%s>." % (
                            value, type(value)))
    
    def parse_datetime(self, value):
        """A lazy method to parse anything to datetime.
        
        Usage::
        
            >>> from weatherlab.lib.timelib.timewrapper import timewrapper
            >>> from datetime import date
            >>> timewrapper.parse_datetime("2001-09-11 10:07:00 AM")
            datetime.datetime(2001, 9, 11, 10, 7)
            >>> timewrapper.parse_datetime(1000217220.0)
            datetime.datetime(2001, 9, 11, 10, 7)
            >>> timewrapper.parse_datetime(date(2001, 9, 11))
            datetime.datetime(2001, 9, 11, 0, 0)
        """
        if isinstance(value, str):
            return self.str2datetime(value)
        elif isinstance(value, int):
            return self.fromtimestamp(value)
        elif isinstance(value, float):
            return self.fromtimestamp(value)
        elif isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        else:
            raise Exception("Unable to parse datetime from: %s, type<%s>." % (
                            value, type(value)))
    
    #############################
    # datetime object generator #
    #############################
    def _freq_parser(self, freq):
        """
        day, hour, min, sec,
        """
        try:
            if "day" in freq:
                freq = freq.replace("day", "")
                return timedelta(days=int(freq))
            elif "hour" in freq:
                freq = freq.replace("hour", "")
                return timedelta(hours=int(freq))
            elif "min" in freq:
                freq = freq.replace("min", "")
                return timedelta(minutes=int(freq))
            elif "seconds" in freq:
                freq = freq.replace("seconds", "")
                return timedelta(seconds=int(freq))
            else:
                raise Exception("%s is invalid format. use day, hour, min, sec." % freq)
        except:
            raise Exception("%s is invalid format. use day, hour, min, sec." % freq)
        
    def dtime_range(self, start=None, end=None, periods=None, 
                    freq="1day", normalize=False):
        """A pure Python implementation of pandas.date_range().
        Given 2 of start, end, periods and freq, generate a series of 
        datetime object.
        
        :param start: Left bound for generating dates
        :type start: str or datetime.datetime (default None)
        
        :param end: Right bound for generating dates
        :type end: str or datetime.datetime (default None)
                
        :param periods: Number of date points. If None, must specify start 
            and end
        :type periods: integer (default None)
                
        :param freq: string, default '1day' (calendar daily)
            Available mode are day, hour, min, sec
            Frequency strings can have multiples. e.g.
                '7day', '6hour', '5min', '4sec'
        :type freq: string (default '1day' calendar daily)

        :param normalize: Trigger that normalize start/end dates to midnight
        :type normalize: boolean (default False)
        
        :return: A list of datetime.datetime object. An evenly sampled time
            series.
            
        Usage::
            
            >>> from __future__ print_function
            >>> from weatherlab.lib.timelib.timewrapper import timewrapper
            >>> for dt in timewrapper.dtime_range("2014-1-1", "2014-1-7"):
            ...     print(dt)
            2014-01-01 00:00:00
            2014-01-02 00:00:00
            2014-01-03 00:00:00
            2014-01-04 00:00:00
            2014-01-05 00:00:00
            2014-01-06 00:00:00
            2014-01-07 00:00:00
            
        **中文文档**
        
        生成等间隔的时间序列。
        
        需要给出, "起始", "结束", "数量"中的任意两个。以及指定"频率"。以此唯一
        确定一个等间隔时间序列。"频率"项所支持的命令字符有"7day", "6hour", 
        "5min", "4sec" (可以改变数字).
        """
        def normalize_datetime_to_midnight(dtime):
            """normalize a datetime %Y-%m-%d %H:%M:%S to %Y-%m-%d 00:00:00
            """
            return datetime(dtime.year, dtime.month, dtime.day)
        
        def not_normalize(dtime):
            """do not normalize
            """
            return dtime
        
        # if two of start, end, or periods exist
        if (bool(start) + bool(end) + bool(periods)) == 2:
            if normalize:
                converter = normalize_datetime_to_midnight
            else:
                converter = not_normalize
            
            interval = self._freq_parser(freq)
            
            if (bool(start) & bool(end)): # start and end
                if isinstance(start, str): # if str, convert to datetime
                    start = self.str2datetime(start)
                elif not isinstance(start, datetime): 
                    raise Exception("start has to be datetime str or datetime")
                
                if isinstance(end, str): # if str, convert to datetime
                    end = self.str2datetime(end)
                elif not isinstance(end, datetime): 
                    raise Exception("end has to be datetime str or datetime")
                
                if start > end: # if start time later than end time, raise error
                    raise Exception("start time has to be eariler and equal "
                                    "than end time")
                start = start - interval
                
                while 1:
                    start += interval
                    if start <= end:
                        yield converter(start)
                    else:
                        break
                    
            elif (bool(start) & bool(periods)): # start and periods
                if isinstance(start, str): # if str, convert to datetime
                    start = self.str2datetime(start)
                elif not isinstance(start, datetime): 
                    raise Exception("start has to be datetime str or datetime")
                start = start - interval
                for _ in range(periods):
                    start += interval
                    yield converter(start)
                    
            elif (bool(end) & bool(periods)): # end and periods
                if isinstance(end, str): # if str, convert to datetime
                    end = self.str2datetime(end)
                elif not isinstance(end, datetime): 
                    raise Exception("end has to be datetime str or datetime")
                start = end - interval * periods
                for _ in range(periods):
                    start += interval
                    yield converter(start)

        else:
            raise Exception("Must specify two of start, end, or periods")

    """
    在数据库中, 我们经常需要使用:
        SELECT * FROM tablename WHERE create_datetime BETWEEN 'start' and 'end';
    为了方便, 我们提供了day_interval, month_interval, year_interval三个函数能够方便的生成start和end
    日期字符串。例如: month_interval(2014, 3) returns:
        start = "2014-03-01 00:00:00", end = "2014-03-31 23:59:59"
    
    [Notice]
    --------
        生成等间距的datetime序列, 可以使用pandas.date_range函数, 请参考pandas.date_range的部分
    """
    
    @staticmethod
    def day_interval(year, month, day, mode = "str"):
        """Example:
        day_interval(2014, 3, 1, "str") returns: "2014-03-01 00:00:00", 
        "2014-03-01 23:59:59"
        
        str mode return pair of datetime str
        dt mode return pair of datetime object
        """
        start, end = datetime(year, month, day), datetime(year, month, day) + timedelta(days=1) - timedelta(seconds=1)
        if mode == "datetime":
            return start, end
        elif mode == "str":
            return str(start), str(end)
        else:
            raise ModeError(mode)
    
    @staticmethod
    def month_interval(year, month, mode = "str"):
        """Example:
        month_interval(2014, 12, "str") returns: "2014-12-01 00:00:00", 
        "2014-12-31 23:59:59"
        
        str mode return pair of datetime str
        dt mode return pair of datetime object
        """
        if month == 12:
            start, end = datetime(year, month, 1), datetime(year+1, 1, 1) - timedelta(seconds=1)
        else:
            start, end = datetime(year, month, 1), datetime(year, month+1, 1) - timedelta(seconds=1)
        if mode == "datetime":
            return start, end
        elif mode == "str":
            return str(start), str(end)
        else:
            raise ModeError(mode)
        
    @staticmethod
    def year_interval(year, mode = "str"):
        """Example:
        year_interval(2014, "str") returns: "2014-01-01 00:00:00", 
        "2014-12-31 23:59:59"
        
        str mode return pair of datetime str
        dt mode return pair of datetime object
        """
        start, end = datetime(year, 1, 1), datetime(year+1, 1, 1) - timedelta(seconds=1)
        if mode == "datetime":
            return start, end
        elif mode == "str":
            return str(start), str(end)
        else:
            raise ModeError(mode)
        
    ###################################
    # random datetime, date generator #
    ###################################
    def randdate(self, start=date(1970, 1, 1), end=date.today()):
        """Generate a random date between ``start`` to ``end``.

        :param start: Left bound
        :type start: string or datetime.date, (default date(1970, 1, 1))
        :param end: Right bound
        :type end: string or datetime.date, (default date.today())
        :return: a datetime.date object
        
        **中文文档**
        
        随机生成一个位于 ``start`` 和 ``end`` 之间的日期。
        """
        if isinstance(start, str):
            start = self.str2date(start)
        if isinstance(end, str):
            end = self.str2date(end)
        if start > end:
            raise Exception("start must be smaller than end! "
                            "your start=%s, end=%s" % (start, end))
        return date.fromordinal(random.randint(start.toordinal(), end.toordinal()))

    def randdatetime(self, start=datetime(1970,1,1), end=datetime.now()):
        """Generate a random datetime between ``start`` to ``end``.

        :param start: Left bound
        :type start: string or datetime.datetime, (default datetime(1970, 1, 1))
        :param end: Right bound
        :type end: string or datetime.datetime, (default datetime.now())
        :return: a datetime.datetime object
        
        **中文文档**
        
        随机生成一个位于 ``start`` 和 ``end`` 之间的时间。
        """
        if isinstance(start, str):
            start = self.str2datetime(start)
        if isinstance(end, str):
            end = self.str2datetime(end)
        if start > end:
            raise Exception("start must be smaller than end! your start=%s, end=%s" % (start, end))
        return datetime.fromtimestamp(random.randint(self.totimestamp(start), self.totimestamp(end)))

timewrapper = TimeWrapper()

############
# Unittest #
############

if __name__ == "__main__":
    import unittest

    class TemplateUnittest(unittest.TestCase):
        def test_all(self):
            for pattern, example in _DATE_TEMPLATE.items():
                datetime.strptime(example, pattern).date()
            
            for pattern, example in _DATETIME_TEMPLATE.items():
                datetime.strptime(example, pattern)

    class TimeWrapperUnittest(unittest.TestCase):
        def test_reformat(self):
            self.assertEqual(timewrapper.reformat("2014-01-05", "%Y-%m-%d", "%d/%m/%Y"),
                             "05/01/2014")
            self.assertEqual(timewrapper.reformat("2014-01-05 19:45:32", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d"),
                             "2014/01/05")
        
        def test_str2date(self):
            self.assertEqual(timewrapper.std_datestr("September 20, 2014"), 
                             "2014-09-20")
            self.assertEqual(timewrapper.std_datestr("Sep 20, 2014"), 
                             "2014-09-20")
            self.assertRaises(NoMatchingTemplateError, 
                              timewrapper.std_datestr, "[2014][05][01]")
        
        def test_str2datetime(self):
            self.assertEqual(
                timewrapper.std_datetimestr("2014-07-13 8:12:34"), 
                "2014-07-13 08:12:34",
                )
            
            self.assertEqual(
                timewrapper.std_datetimestr("2014-07-13 8:12:34 PM"), 
                "2014-07-13 20:12:34",
                )
            
            self.assertRaises(
                NoMatchingTemplateError, 
                timewrapper.std_datetimestr, "[2014][07][13]",
                )
        
        def test_toordinal_fromordinal(self):
            a_date = date(1920, 8, 23)
            self.assertEqual(a_date.toordinal(),
                             timewrapper.toordinal(a_date))
            self.assertEqual(date.fromordinal(701135),
                             timewrapper.fromordinal(701135))
            
        def test_totimestamp_fromtimestamp(self):
            """test totimestamp and fromtimestamp method
            """
            a_datetime = datetime(1997, 7, 7, 12, 0, 0)
            try:
                self.assertEqual(a_datetime.timestamp(), 
                                 timewrapper.totimestamp(a_datetime))
                self.assertEqual(datetime.fromtimestamp(123456789), 
                                 timewrapper.fromtimestamp(123456789))
            except:
                self.assertEqual(868291200, 
                                 timewrapper.totimestamp(a_datetime))
                self.assertEqual(datetime.fromtimestamp(123456789), 
                                 timewrapper.fromtimestamp(123456789))
                 
            a_datetime = datetime(1924, 2, 19, 12, 0, 0)
            try:
                self.assertEqual(a_datetime.timestamp(), 
                                 timewrapper.totimestamp(a_datetime))
                self.assertEqual(datetime.fromtimestamp(-123456789), 
                                 timewrapper.fromtimestamp(-123456789))
            except:
                self.assertEqual(-1447401600, 
                                 timewrapper.totimestamp(a_datetime))
                self.assertEqual(datetime(1966, 2, 1, 22, 26, 51), 
                                 timewrapper.fromtimestamp(-123456789))
        
        def test_parser(self):
            """test universal parser
            """
            self.assertEqual(
                timewrapper.parse_date("10-1-1949"), date(1949, 10, 1))
            self.assertEqual(
                timewrapper.parse_date(711766), date(1949, 10, 1))
            self.assertEqual(
                timewrapper.parse_date(datetime(1949, 10, 1, 8, 15, 0)), 
                date(1949, 10, 1))

            self.assertEqual(
                timewrapper.parse_datetime("1949-10-1 8:15:00"), 
                datetime(1949, 10, 1, 8, 15),
                )
            self.assertEqual(
                timewrapper.parse_datetime(-639056700), 
                datetime(1949, 10, 1, 8, 15),
                )
            self.assertEqual(
                timewrapper.parse_datetime(-639056700.0), 
                datetime(1949, 10, 1, 8, 15),
                )
            self.assertEqual(
                timewrapper.parse_datetime(date(1949, 10, 1)), 
                datetime(1949, 10, 1),
                )

        def test_dtime_range(self):
            """test dtime_range generator method
            """
            # test start + end
            self.assertListEqual(
                [
                    datetime(2014,1,1,3,0,0), 
                    datetime(2014,1,1,3,5,0), 
                    datetime(2014,1,1,3,10,0),
                ],
                list(timewrapper.dtime_range(
                                    start="2014-01-01 03:00:00", 
                                    end="2014-01-01 03:10:00", 
                                    freq="5min")),
                )
            
            # test start + periods
            self.assertListEqual(
                [
                    datetime(2014,1,1,3,0,0), 
                    datetime(2014,1,1,3,5,0), 
                    datetime(2014,1,1,3,10,0),
                ],
                list(timewrapper.dtime_range(
                                    start="2014-01-01 03:00:00", 
                                    periods=3, 
                                    freq="5min")),
                )
            # test end + periods
            self.assertListEqual(
                [
                    datetime(2014,1,1,3,0,0), 
                    datetime(2014,1,1,3,5,0), 
                    datetime(2014,1,1,3,10,0),
                ],
                list(timewrapper.dtime_range(
                                    end="2014-01-01 03:10:00",
                                    periods=3,
                                    freq="5min")),
                )
            
            # test take datetime as input
            self.assertListEqual(
                [
                    datetime(2014,1,1,3,0,0), 
                    datetime(2014,1,1,3,5,0), 
                    datetime(2014,1,1,3,10,0),
                ],
                list(timewrapper.dtime_range(
                                    start=datetime(2014,1,1,3,0,0), 
                                    end=datetime(2014,1,1,3,10,0), 
                                    freq="5min")),
                )

        def test_day_month_year_interval(self):
            # === day_interval ===
            # with no mode argument
            self.assertTupleEqual(
                timewrapper.day_interval(2014, 3, 5),
                ("2014-03-05 00:00:00", "2014-03-05 23:59:59")
                )
            
            # datetime mode
            self.assertTupleEqual(
                timewrapper.day_interval(2014, 12, 31, mode="datetime"),
                (datetime(2014,12,31,0,0,0), datetime(2014,12,31,23,59,59))
                )
            
            # wrong mode
            self.assertRaises(
                ModeError, timewrapper.day_interval, 2014, 12, 31, mode="good") 
        
            # === month_interval ===
            self.assertTupleEqual(
                timewrapper.month_interval(2014, 3),
                ("2014-03-01 00:00:00", "2014-03-31 23:59:59")
                )
            
            self.assertTupleEqual(
                timewrapper.month_interval(2014, 12, mode="datetime"),
                (datetime(2014,12,1,0,0,0), datetime(2014,12,31,23,59,59))
                )
            
            self.assertRaises(
                ModeError, timewrapper.month_interval, 2014, 12, mode="good")
            
            # === year interval ===
            self.assertTupleEqual(
                timewrapper.year_interval(2014),
                ("2014-01-01 00:00:00", "2014-12-31 23:59:59")
                )
            
            self.assertTupleEqual(
                timewrapper.year_interval(2014, mode="datetime"),
                (datetime(2014,1,1,0,0,0), datetime(2014,12,31,23,59,59))
                )
            
            self.assertRaises(
                ModeError, timewrapper.year_interval, 2014, mode="good")

        def test_randdate_randdatetime(self):
            # test random date is between the boundary
            a_date = timewrapper.randdate("2014-01-01", date(2014, 1, 31))
            self.assertGreaterEqual(a_date, date(2014, 1, 1))
            self.assertLessEqual(a_date, date(2014, 1, 31))
 
            # test random datetime is between the boundary
            a_datetime = timewrapper.randdatetime("2014-01-01", datetime(2014, 1, 31, 23, 59, 59))
            self.assertGreaterEqual(a_datetime, datetime(2014, 1, 1, 0, 0, 0))
            self.assertLessEqual(a_datetime, datetime(2014, 1, 31, 23, 59, 59))

    unittest.main()