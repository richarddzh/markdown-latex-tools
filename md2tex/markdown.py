'''
markdown.py
  - author: Richard Dong
  - description: A very simple markdown parser with limited support
'''

import re

class State:
  TEXT = 0
  TABLE = 1
  COMMENT = 2
  EQUATION = 3
  CODE = 4

class Parser:
  def __init__(self):
    self._state = State.TEXT
    self._list_stack = list()
    self._title = re.compile(r'^\s*(#+)\s*(.+)$')
    self._image = re.compile(r'^\s*!\[([^\]]*)\]\(([^\)]+)\)\s*$')
    self._table = re.compile(r'^\s*\|([^\|]+\|)+\s*$')
    self._table_cell = re.compile(r'\s*\|\s*([^\|]*)')
    self._table_line = re.compile(r'^(\s*\|)+\s*-((\s|-)*\|)+\s*$')
    self._comment = re.compile(r'<!--.*?(?=-->)-->')
    self._equation = re.compile(r'^\s*\$\$\s*$')
    self._list = re.compile(r'^(\s*)([0-9]+\.|-|\+|\*)\s+(.+)$')
    self._include = re.compile(r'^\s*\*\s*\[([^\]]*)\]\(([^\)]+)\.md\)\s*$')
    self._code = re.compile(r'^\s*```(\S*)\s*$')
    self._newline = re.compile(r'\n\r?')

  def parse(self, text):
    for line in self._newline.split(text):
      self.parse_line(line)
    self.parse_line('')

  def parse_line(self, line):
    line = line.rstrip('\n\r')
    if self.try_end_comment(line): return
    if self.try_comment(line): return
    self.parse_line_commentless(line)

  def parse_line_commentless(self, line):
    if self.try_include(line): return
    if self.try_equation(line): return
    if self.try_code(line): return
    if self.try_title(line): return
    if self.try_include(line): return
    if self.try_image(line): return
    if self.try_table(line): return
    if self.try_list(line): return
    self.parse_text(line)

  def set_state(self, s):
    if s == self._state: return
    if self._state == State.TABLE:
      self.handler.on_end_table()
    if self._state == State.EQUATION:
      self.handler.on_end_equation()
    if self._state == State.CODE:
      self.handler.on_end_code()
    if s == State.TABLE:
      self.handler.on_begin_table()
    if s == State.EQUATION:
      self.handler.on_begin_equation()
    self._state = s

  def parse_text(self, text):
    self.set_state(State.TEXT)
    self.handler.on_text(text)

  def try_comment(self, line):
    if '<!--' not in line: return False
    m = self._comment.split(line)
    pos = m[-1].find('<!--')
    if pos >= 0:
      last_comment = m[-1][pos:]
      m[-1] = m[-1][0:pos]
    t = ''.join(m)
    if len(t) > 0 and (not t.isspace()): self.parse_line_commentless(t)
    for c in self._comment.findall(line):
      self.handler.on_comment(c)
    if pos >= 0:
      self.handler.on_comment(last_comment)
      self.set_state(State.COMMENT)
    return True

  def try_end_comment(self, line):
    if self._state != State.COMMENT: return False
    pos = line.find('-->')
    if pos < 0:
      self.handler.on_comment(line)
    else:
      self.handler.on_comment(line[:pos + 3])
      self.set_state(State.TEXT)
      t = line[pos + 3:]
      if len(t) > 0 and (not t.isspace()): self.parse_line(t)
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
      m.pop()
      self.handler.on_table_row(m)
    else:
      self.handler.on_table_line()
    return True

  def try_equation(self, line):
    m = self._equation.match(line)
    if self._state == State.EQUATION and m is None:
      self.handler.on_equation(line)
    elif self._state == State.EQUATION:
      self.set_state(State.TEXT)
    elif m is None:
      return False
    else:
      self.set_state(State.EQUATION)
    return True

  def try_code(self, line):
    m = self._code.match(line)
    if self._state == State.CODE and m is None:
      self.handler.on_code(line)
    elif self._state == State.CODE:
      self.set_state(State.TEXT)
    elif m is None:
      return False
    else:
      self.set_state(State.CODE)
      self.handler.on_begin_code(m.group(1))
    return True

  def try_list(self, line):
    if line.isspace() or len(line) == 0:
      while self._list_stack:
        self.handler.on_end_list(self._list_stack[-1][0])
        self._list_stack.pop()
      return False
    m = self._list.match(line)
    if m is None: return False
    self.set_state(State.TEXT)
    symbol = m.group(2)
    depth = len(m.group(1))
    text = m.group(3)
    while self._list_stack and self._list_stack[-1][1] > depth:
      self.handler.on_end_list(self._list_stack[-1][0])
      self._list_stack.pop()
    if (not self._list_stack) or self._list_stack[-1][1] < depth:
      self._list_stack.append((symbol, depth))
      self.handler.on_begin_list(symbol)
    self.handler.on_list_item(symbol)
    self.parse_text(text)
    return True

  def try_include(self, line):
    m = self._include.match(line)
    if m is None: return False
    self.handler.on_include(m.group(2))
    return True

