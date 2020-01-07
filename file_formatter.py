"""
Format file content by line.

E.g. Input line: a,b,c
Output line: {a},{b},{c}

The format is up to you.
"""

from os import path
from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string('src', None, 'Source file name')
flags.DEFINE_string('tar', None, 'Target file name')
flags.DEFINE_string('mod', None, 'Write mode: A-append|T-truncate')


def line_formatter(line, lineno):
    """

    :param lineno: int
    :type line: str
    :return str
    """
    if lineno == 0:
        return line
    line = line.rstrip('\n')
    deli = '\t'
    parts = line.split(deli)
    new_parts = []
    for i, p in enumerate(parts):
        if i == 0:
            new_parts.append(p)
        else:
            p = '' if p == '\N' else p
            new_parts.append('{%s}' % p)
    return deli.join(new_parts) + '\n'


class FileFormatter:
    def __init__(self, fname, target):
        self.filename = fname
        self.target = target
        self.formatter = None
        self.append = False
    
    def set_formatter(self, formatter):
        self.formatter = formatter
        
    def set_append(self, b):
        self.append = b
        
    def formatter(self):
        fh = open(self.filename, 'r')
        th = open(self.target, 'a+' if self.append else 'w+')
        while True:
            line = fh.readline()
            fline = self.formatter(line)
            th.write(fline)
            
    def run(self):
        if not path.isfile(self.filename):
            print('Error: \'%s\' not a valid file' % self.filename)
            return
        try:
            th = open(self.target, 'a+' if self.append else 'w+')
        except FileNotFoundError as e:
            print('Error: %s' % str(e))
            return
        fh = open(self.filename, 'r')
        file_size = path.getsize(self.filename)
        print('File size(byte): %d' % file_size)
        print('Write mode: %s' % ('append' if self.append else 'truncate'))
        read_size = 0
        percent = 0
        print('Progress: ')
        lineno = 0
        while True:
            line = fh.readline()
            if len(line) == 0:
                break
            fline = self.formatter(line, lineno)
            th.write(fline)
            read_size += len(line)
            now_percent = float(read_size * 100) / file_size
            if now_percent - percent >= 1:
                percent = now_percent
                print('--> %d%% ' % int(now_percent), end='')
            lineno += 1
        fh.close()
        th.close()
        
        
def main(argv):
    if FLAGS.src is None:
        print('Miss source filename')
        return
    if FLAGS.tar is None:
        print('Miss target filename')
        return
    if FLAGS.mod is None:
        print('Miss write mode')
        return
    fm = FileFormatter(FLAGS.src, FLAGS.tar)
    fm.set_formatter(line_formatter)
    fm.set_append(FLAGS.mod == 'A')
    fm.run()
    
        
if __name__ == '__main__':
    app.run(main)
