'''
md2tex.py
 - author: Richard Dong
 - description: Convert markdown to latex
'''
import re
import fileinput
import markdown

class Handler:
  def on_begin_table(self):
    print('begin table')

  def on_end_table(self):
    print('end table')

  def on_text(self, text):
    print('text: ' + text)

  def on_comment(self, comment):
    print('comment: ' + comment)

  def on_title(self, **arg):
    print('title' + str(arg['level']) + ': ' + arg['title'])

  def on_image(self, **arg):
    print('image ' + arg['url'] + ': ' + arg['caption'])

  def on_table_line(self):
    print('table line')

  def on_table_row(self, row):
    print('table row: ' + str(row))

  def on_begin_equation(self):
    print('begin equation')

  def on_end_equation(self):
    print('end equation')

  def on_equation(self, equ):
    print('equation: ' + equ)

  def on_begin_list(self, sym):
    print('begin list: ' + sym)

  def on_end_list(self, sym):
    print('end list: ' + sym)

  def on_list_item(self, sym):
    print('list item: ' + sym)

p = markdown.Parser()
p.handler = Handler()
for line in fileinput.input():
  p.parse_line(line)
