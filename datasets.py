"""
Generate datasets for databases, initially for PostgreSQL.
Usage:
  python datasets.py --tar='datasets.txt' --delim=tab --num=10 --columns='a:int[],b:int,c:text'
Supported data types:
  text - text
  text[] - text[]
  integer - int
  integer[] - int[]
  json - json, embedded object not supported
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

"""
Required flags
"""
flags.DEFINE_string('tar', None, 'Target file name')
flags.DEFINE_string('delim', None, 'Delimiter')
flags.DEFINE_string('num', None, 'Data number')
flags.DEFINE_string('columns', None, 'Columns definition. E.g. name:text,age:integer')

"""
Optional flags
"""
flags.DEFINE_string('enum_cards', None, 'Enumerate cards. E.g. A,B,C,D,E')
flags.DEFINE_string('json_schema', None, 'JSON schema. E.g. tags:text[],name:text')
flags.DEFINE_string('int_low', None, 'Integer lower bound')
flags.DEFINE_string('int_up', None, 'Integer upper bound')
flags.DEFINE_string('int_array_len_low', None, 'Integer array length lower bound')
flags.DEFINE_string('int_array_len_up', None, 'Integer array length upper bound')
flags.DEFINE_string('int_array_elem_low', None, 'Integer array element lower bound')
flags.DEFINE_string('int_array_elem_up', None, 'Integer array element upper bound')
flags.DEFINE_string('timestamp_low', None, 'Timestamp lower bound')
flags.DEFINE_string('timestamp_delta', None, 'Timestamp delta in days')

FAKER = Faker()

# column delimiter
supported_delims = {
    'tab': '\t',
    'space': '    ',
}


class ColumnError(Exception):
    """
    """


class DelimError(Exception):
    """
    """


class Parameters(object):
    """
    runtime parameters
    """
    def __init__(self):
        self.enum_cards = ['bad', 'ok', 'good']
        self.json_schema = {"name": "text", "tags": "text[]"}
        self.integer_low = 900
        self.integer_up = 1000
        self.text_array_len_low = 3
        self.text_array_len_up = 10
        self.integer_array_len_low = 3
        self.integer_array_len_up = 10
        self.integer_array_elem_low = 100
        self.integer_array_elem_up = 200
        self.timestamp_low = date(2019, 12, 1)
        self.timestamp_delta = timedelta(30)


class Array(object):
    def __init__(self, arr):
        self.value = arr
    
    def __str__(self):
        for i, _ in enumerate(self.value):
            self.value[i] = str(self.value[i])
        return '{' + ','.join(self.value) + '}'
    
    def value_of(self):
        return self.value


def int_array(p):
    """

    :type p: Parameters
    """
    arr = list()
    ran = random.randint(p.integer_array_len_low, p.integer_array_len_up)
    for i in range(ran):
        arr.append(integer(p, p.integer_array_elem_low, p.integer_array_elem_up))
    return Array(arr)


def text_array(p):
    """

    :type p: Parameters
    """
    arr = list()
    ran = random.randint(p.text_array_len_low, p.text_array_len_up)
    for i in range(ran):
        arr.append(word(p))
    return Array(arr)


def word(p):
    return FAKER.word()


def integer(p, low=None, up=None):
    """
    
    :param up:
    :param low:
    :type p: Parameters
    :param p:
    :return:
    """
    lb = p.integer_low if low is None else low
    ub = p.integer_up if up is None else up
    return random.randint(lb, ub)


def timestamp(p):
    """

    :type p: Parameters
    """
    offset = random.randint(0, p.timestamp_delta.days)
    h, m, s = random.randint(0, 23), random.randint(0, 59), random.randint(0, 59)
    return str(p.timestamp_low + timedelta(days=offset)) + ' ' + str(time(h, m, s))


def timestamp_int(p):
    """

    :type p: Parameters
    """
    offset = random.randint(0, p.timestamp_delta.days)
    h, m, s = random.randint(0, 23), random.randint(0, 59), random.randint(0, 59)
    dt = p.timestamp_low + timedelta(days=offset)
    return int(datetime(dt.year, dt.month, dt.day, h, m, s).timestamp())


def enum(p):
    """

    :type p:  Parameters
    """
    return p.enum_cards[random.randint(0, len(p.enum_cards) - 1)]


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


def parse_enum_cards(cards):
    return cards.split(',')


def parse_json_schema(schema):
    return parse_columns(schema)


def _json(p):
    """

    :type p: Parameters
    """
    js = dict()
    for _, f in enumerate(p.json_schema):
        v = type_method_map[p.json_schema[f]](p)
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
    params = Parameters()
    while i < num:
        i += 1
        row = list()
        for _, c in enumerate(col_methods):
            row.append(str(col_methods[c](params)))
        fh.write(delim.join(row) + '\n')


if __name__ == '__main__':
    app.run(main)
