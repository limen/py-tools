"""
Generate datasets for databases, initially for PostgreSQL.
Usage:
  python datasets.py --tar='datasets.txt' --delim=tab --num=10 --columns='a:int[],b:int,c:text'
Supported data types:
  text - text
  text[] - text[]
  integer - int
  integer[] - int[]
  json - json
  enum - enum
  timestamp - ts
  timestamp in seconds - tsint
Todo data types:
  point
  line
  circle

"""
from faker import Faker
import random
from datetime import datetime, timedelta, date, time
from absl import app
from absl import flags
import json

FLAGS = flags.FLAGS
flags.DEFINE_string('tar', None, 'Target file name')
flags.DEFINE_string('delim', None, 'Delimiter')
flags.DEFINE_string('num', None, 'Data number')
flags.DEFINE_string('columns', None, 'Columns definition. E.g. name:text,age:integer')

FAKER = Faker()

# 时间戳范围
ts_low = date(2019, 12, 1)
ts_up = date(2020, 1, 7)
ts_delta = ts_up - ts_low
# 枚举定义
enum_cards = ['A', 'B', 'C', 'D', 'E']
enum_cards_num = len(enum_cards)
# 分割符
supported_delims = {
    'tab': '\t',
    'space': '    ',
}
# json schema
json_schema = {
    'tags': 'text[]',
    'name': 'text'
}


class ColumnError(Exception):
    """
    """


class DelimError(Exception):
    """
    """


class Array(object):
    def __init__(self, arr):
        self.value = arr
    
    def __str__(self):
        for i, _ in enumerate(self.value):
            self.value[i] = str(self.value[i])
        return '{' + ','.join(self.value) + '}'
    
    def value_of(self):
        return self.value


def int_array(length=10, low=0, up=100):
    arr = list()
    for i in range(length):
        arr.append(integer(low, up))
    return Array(arr)


def text_array(length=10):
    arr = list()
    for i in range(length):
        arr.append(word())
    return Array(arr)


def word():
    return FAKER.word()


def integer(low=0, up=100):
    return random.randint(low, up)


def timestamp():
    offset = random.randint(0, ts_delta.days)
    h, m, s = random.randint(0, 23), random.randint(0, 59), random.randint(0, 59)
    return str(ts_low + timedelta(days=offset)) + ' ' + str(time(h, m, s))


def timestamp_int():
    offset = random.randint(0, ts_delta.days)
    h, m, s = random.randint(0, 23), random.randint(0, 59), random.randint(0, 59)
    dt = ts_low + timedelta(days=offset)
    return int(datetime(dt.year, dt.month, dt.day, h, m, s).timestamp())


def enum():
    return enum_cards[random.randint(0, enum_cards_num - 1)]


def parse_columns(columns):
    columns = columns.split(',')
    col_methods = dict()
    for _, v in enumerate(columns):
        try:
            col, tp = v.split(':')
            col_methods[col] = type_method_map[tp]
        except ValueError:
            raise ColumnError('not valid column definition: ' + v)
        except KeyError:
            raise ColumnError('not supported column type: ' + tp)
    return col_methods


def parse_delim(delim):
    try:
        char = supported_delims[delim]
    except KeyError:
        raise DelimError('not supported delimiter:' + delim)
    return char


def _json():
    js = dict()
    for _, f in enumerate(json_schema):
        v = type_method_map[json_schema[f]]()
        js[f] = v.value_of() if isinstance(v, Array) else v
    return json.dumps(js)


type_method_map = {
    "text": word,
    "ts": timestamp,
    "enum": enum,
    "int[]": int_array,
    "text[]": text_array,
    "int": integer,
    "json": _json,
    "tsint": timestamp_int,
}


def main(argv):
    if FLAGS.tar is None:
        print("Miss target file param")
        return
    if FLAGS.delim is None:
        print("Miss delimiter param")
        return
    if FLAGS.num is None:
        print("Miss data number param")
        return
    if FLAGS.columns is None:
        print("Miss columns param")
        return
    try:
        delim = parse_delim(FLAGS.delim)
    except DelimError as e:
        print("Delimiter error: " + str(e))
        return
    try:
        col_methods = parse_columns(FLAGS.columns)
    except ColumnError as e:
        print("Columns definition error: " + str(e))
        return
    i = 0
    num = int(FLAGS.num)
    try:
        fh = open(FLAGS.tar, 'a+')
    except FileNotFoundError as e:
        print('Error: %s' % str(e))
        return
    while i < num:
        i += 1
        row = list()
        for _, c in enumerate(col_methods):
            row.append(str(col_methods[c]()))
        fh.write(delim.join(row) + '\n')


if __name__ == '__main__':
    app.run(main)
