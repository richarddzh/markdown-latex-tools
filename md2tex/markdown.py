'''
markdown.py
  - author: Richard Dong
  - description: A very simple markdown parser
'''

import re

class State:
  TEXT = 0
  TABLE = 1
  COMMENT = 2

class Parser:
  def __init__(self):
    self.state = State.TEXT
    self._title = re.compile(r'^\s*(#+)\s*(.+)$')
    self._image = re.compile(r'^\s*!\[([^\]]*)\]\(([^\)]+)\)\s*$')
    self._table = re.compile(r'^\s*\|([^\|]+\|)+\s*$')
    self._table_cell = re.compile(r'\s*\|\s*([^\|]*)')
    self._table_line = re.compile(r'^(\s*\|)+\s*-((\s|-)*\|)+\s*$')
    self._comment = re.compile(r'<!--.*?(?=-->)-->')

  def parse_line(self, line):
    line = line.rstrip('\n\r')
    if self.try_end_comment(line): return
    if self.try_comment(line): return
    self.parse_line_commentless(line)

  def parse_line_commentless(self, line):
    if self.try_title(line): return
    if self.try_image(line): return
    if self.try_table(line): return
    self.parse_text(line)

  def set_state(self, s):
    if s == self.state: return
    if s == State.TABLE:
      self.handler.on_begin_table()
    if self.state == State.TABLE:
      self.handler.on_end_table()
    self.state = s

  def parse_text(self, text):
    self.set_state(State.TEXT)
    self.handler.on_text(text)

  def try_comment(self, line):
    if '<!--' not in line: return False
    m = self._comment.split(line)
    pos = m[len(m) - 1].find('<!--')
    if pos >= 0:
      last_comment = m[len(m) - 1][pos:]
      m[len(m) - 1] = m[len(m) - 1][0:pos]
    t = ''.join(m)
    if len(t) > 0 and (not t.isspace()): self.parse_line_commentless(t)
    for c in self._comment.findall(line):
      self.handler.on_comment(c)
    if pos >= 0:
      self.handler.on_comment(last_comment)
      self.set_state(State.COMMENT)
    return True

  def try_end_comment(self, line):
    if self.state != State.COMMENT: return False
    pos = line.find('-->')
    if pos < 0:
      self.handler.on_comment(line)
    else:
      self.handler.on_comment(line[:pos + 3])
      self.set_state(State.TEXT)
      self.parse_line(line[pos + 3:])
    return True

  def try_title(self, line):
    m = self._title.match(line)
    if m is None: return False
    self.set_state(State.TEXT)
    self.handler.on_title(level=len(m.group(1)), title=m.group(2))
    return True

  def try_image(self, line):
    m = self._image.match(line)
    if m is None: return False
    self.set_state(State.TEXT)
    self.handler.on_image(caption=m.group(1), url=m.group(2))
    return True

  def try_table(self, line):
    m = self._table.match(line)
    if m is None: return False
    self.set_state(State.TABLE)
    m = self._table_line.match(line)
    if m is None:
      m = self._table_cell.findall(line)
      del m[len(m) - 1]
      self.handler.on_table_row(m)
    else:
      self.handler.on_table_line()
    return True
