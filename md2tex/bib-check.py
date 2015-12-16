'''
bib-check.py
 - author: Richard Dong
 - description: Check redundant entries in bib file.
'''

import re
import io
import sys
import argparse

class BibChecker:
  def __init__(self):
    self._entries = set()
    self._line = re.compile(r'^@\s*\w+\s*\{\s*(\w+)\s*,\s*$')
  def check_line(self, line):
    m = self._line.match(line)
    if m is None: return
    m = m.group(1)
    if m in self._entries:
      print('redundant entry: %s' % m)
    else:
      self._entries.add(m)

parser = argparse.ArgumentParser(description='check redundant entries in bib file.')
parser.add_argument('-c', dest='encoding', help='file encoding', default='utf8')
parser.add_argument('file', nargs='*', help='input files')
args = parser.parse_args()

for f in args.file:
  p = BibChecker()
  with io.open(f, mode='rt', encoding=args.encoding) as fi:
    for line in fi:
      p.check_line(line)
  print('finish checking file %s' % f)

if not args.file:
  for line in sys.stdin:
    p.parse_line(line)
  print('finish checking stdin')
