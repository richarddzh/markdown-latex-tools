'''
md2tex.py
 - author: Richard Dong
 - description: Convert markdown to latex
'''
from __future__ import print_function
import re
import io
import sys
import argparse
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
    self._cite = re.compile(r'\[(cite|ref)@\s*([A-Za-z0-9:]+(\s*,\s*[A-Za-z0-9:]+)*)\]')
    self._bold = re.compile(r'\*\*(?!\s)(.+?)\*\*')

  def convert_text(self, text):
    if len(text) == 0 or text.isspace(): return ''
    m = self._inline_math.split(text)
    s = ''
    for i in range(len(m)):
      if len(m[i]) == 0 or m[i].isspace(): continue
      if i % 2 == 0:
        text = self.convert_text_no_math(m[i])
      else:
        text = '$' + m[i] + '$'
      s = s + text
    return s

  def convert_text_no_math(self, text):
    if len(text) == 0 or text.isspace(): return ''
    m = self._bold.split(text)
    s = ''
    for i in range(len(m)):
      if len(m[i]) == 0 or m[i].isspace(): continue
      if i % 2 == 0:
        text = self.convert_text_no_bold(m[i])
      else:
        text = '\\textbf{' + self.convert_text_no_bold(m[i]) + '}'
      s = s + text
    return s

  def convert_text_no_bold(self, text):
    text = self._escape.sub(r'\\\1', text)
    text = text.replace(r'\\', r'\textbackslash{}')
    text = self._cite.sub(r'\\\1{\2}', text)
    return text

  def print_label(self):
    if 'label' in self.vars:
      print('\\label{%s}' % self.vars.pop('label', 'nolabel'))

  def get_float_style(self):
    fl = self.vars.pop('float', '!ht')
    if fl == '!h' or fl == 'h!':
      fl = '!ht'
    return fl

  def on_begin_table(self):
    caption = self.convert_text(self.vars.pop('caption', ''))
    print('\\begin{table}[%s]' % self.get_float_style())
    print('\\caption{%s}' % caption)
    self.print_label()
    print('\\centering\\begin{tabular}{%s}\\hline' % self.vars.pop('columns', 'c'))

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
    print('\\begin{figure}[%s]' % self.get_float_style())
    print('\\centering\\includegraphics[width=%s\\linewidth]{%s}' % (self.vars.pop('width', '0.5'), url))
    print('\\caption{%s}' % caption)
    self.print_label()
    print('\\end{figure}')

  def on_table_line(self):
    print('\\hline')

  def on_table_row(self, row):
    row = [self.convert_text(x) for x in row]
    print(' & '.join(row) + ' \\\\')

  def on_begin_equation(self):
    print('\\begin{equation}')
    self.print_label()

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

  def on_include(self, filename):
    print('\\input{%s.tex}' % filename)

  def on_begin_code(self, lang):
    params = list()
    if lang and not lang.isspace():
      params.append('language=%s' % lang)
    caption = self.convert_text(self.vars.pop('caption', ''))
    if caption and not caption.isspace():
      params.append('caption={%s}' % caption)
    params = ','.join(params)
    if params and not params.isspace():
      params = '[' + params + ']'
    print('\\begin{lstlisting}' + params)

  def on_end_code(self):
    print('\\end{lstlisting}')

  def on_code(self, code):
    print(code)

parser = argparse.ArgumentParser(description='convert markdown to latex.')
parser.add_argument('-c', dest='encoding', help='file encoding', default='utf8')
parser.add_argument('-o', dest='output', help='output file')
parser.add_argument('file', nargs='*', help='input files')
args = parser.parse_args()

if args.output is not None:
  sys.stdout = io.open(args.output, mode='wt', encoding=args.encoding)

for f in args.file:
  p = markdown.Parser()
  p.handler = Handler()
  with io.open(f, mode='rt', encoding=args.encoding) as fi:
    for line in fi:
      p.parse_line(line)
    p.parse_line('')

if not args.file:
  p = markdown.Parser()
  p.handler = Handler()
  for line in sys.stdin:
    p.parse_line(line)
  p.parse_line('')

