'''
md2tex.py
 - author: Richard Dong
 - description: Convert markdown to latex
'''
from __future__ import print_function
import re
import fileinput
import markdown

class State:
  NORMAL = 0
  RAW = 1

class Handler:
  def __init__(self):
    self.vars = dict()
    self.state = State.NORMAL
    self._begin_latex = re.compile(r'^<!-- latex\s*$')
    self._set_vars = re.compile(r'^<!-- set(\s+\w+="[^"]+")+\s*-->$')
    self._var_pair = re.compile(r'(\w+)="([^"]+)"')
    self._escape = re.compile(r'(&|%|\$|_|\{|\})')
    self._inline_math = re.compile(r'\$\$(.+?)\$\$')

  def convert_text(self, text):
    m = self._inline_math.split(text)
    s = ''
    for i in range(len(m)):
      if i % 2 == 0:
        text = self._escape.sub(r'\\\1', m[i])
        text = text.replace(r'\\', r'\textbackslash{}')
      else:
        text = '$' + m[i] + '$'
      s = s + text
    return s

  def on_begin_table(self):
    caption = self.convert_text(self.vars.get('caption', ''))
    print('\\begin{table}[%s]' % self.vars.get('float', '!h'))
    print('\\caption{%s}\\label{%s}' % (caption, self.vars.get('label', 'tab:nolabel')))
    print('\\centering\\begin{tabular}{%s}\\hline' % self.vars.get('columns', 'c'))

  def on_end_table(self):
    print('\\hline\\end{tabular}')
    print('\\end{table}')

  def on_text(self, text):
    print(self.convert_text(text))

  def on_comment(self, comment):
    if self._begin_latex.match(comment):
      self.state = State.RAW
    elif self.state == State.RAW and '-->' in comment:
      self.state = State.NORMAL
    elif self.state == State.RAW:
      print(comment)
    elif self._set_vars.match(comment):
      for (k, v) in self._var_pair.findall(comment):
        self.vars[k] = v

  def on_title(self, **arg):
    level = arg['level']
    title = self.convert_text(arg['title'])
    if level == 1:
      print('\\chapter{%s}' % title)
    else:
      print('\\%ssection{%s}' % ('sub' * (level - 2), title))

  def on_image(self, **arg):
    url = arg['url']
    caption = self.convert_text(arg['caption'])
    print('\\begin{figure}[%s]' % self.vars.get('float', '!h'))
    print('\\centering\\includegraphics[width=%s\\linewidth]{%s}' % (self.vars.get('width', '0.5'), url))
    print('\\caption{%s}\\label{%s}' % (caption, self.vars.get('label', 'fig:nolabel')))
    print('\\end{figure}')

  def on_table_line(self):
    print('\\hline')

  def on_table_row(self, row):
    row = [self.convert_text(x) for x in row]
    print(' & '.join(row) + ' \\\\')

  def on_begin_equation(self):
    print('\\begin{equation}\\label{%s}' % self.vars.get('label', 'equ:nolabel'))

  def on_end_equation(self):
    print('\\end{equation}')

  def on_equation(self, equ):
    print(equ)

  def on_begin_list(self, sym):
    if sym[0].isdigit():
      print('\\begin{enumerate}')
    else:
      print('\\begin{itemize}')

  def on_end_list(self, sym):
    if sym[0].isdigit():
      print('\\end{enumerate}')
    else:
      print('\\end{itemize}')

  def on_list_item(self, sym):
    print('\\item ', end='')

  def on_include(self, file):
    print('\\input{%s.tex}' % file)

p = markdown.Parser()
p.handler = Handler()
for line in fileinput.input():
  p.parse_line(line)
