#!/usr/bin/python

import io, sys, re, os.path
import tempfile
import argparse
import subprocess

def tex_to_png(tex, tempdir, idx, imgdir):
  if len(tex) < 1: return ''
  tex2png = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex2png')
  multiline = False
  if tex[0] == '\n' or tex[0] == '\r': multiline = True
  tmpfname = os.path.join(tempdir, str(idx))
  ftemp = io.open(tmpfname, 'wt')
  ftemp.write(u'\\[' if multiline else u'$')
  ftemp.write(tex)
  ftemp.write(u'\\]' if multiline else u'$')
  ftemp.close()
  ftemp = io.open(tmpfname, 'rt');
  imgname = imgdir + str(idx) + '.png'
  subprocess.call([tex2png, '-i', '-T', '-o', imgname], stdin=ftemp)
  ftemp.close()
  html = r'<!-- ' + tex + ' -->';
  html = html + ('<p>' if multiline else '<span>');
  html = html + '<img src="' + imgname + '">'
  html = html + ('</p>' if multiline else '</span>');
  return html
  

parser = argparse.ArgumentParser(description='Replace LaTeX with images')
parser.add_argument('-i', dest='input', help='markdown file input')
parser.add_argument('-o', dest='output', help='markdown file output')
parser.add_argument('-p', dest='path', help='relative path to store generated images', default='')
parser.add_argument('-e', dest='encoding', help='set encoding for text IO', default='utf-8')
args = parser.parse_args()

fin = sys.stdin
fout = sys.stdout
if args.input != None: fin = io.open(args.input, 'rt', encoding=args.encoding)
if args.output != None: fout = io.open(args.output, 'wt', encoding=args.encoding)

tmpdir = tempfile.mkdtemp()
idx = 0
ineqn = False
tex = ''
dlim = re.compile(r'\$\$')
lines = fin.readlines()
for line in lines:
  start = 0
  for m in dlim.finditer(line):
    if ineqn:
      idx = idx + 1
      fout.write(tex_to_png(tex + line[start:m.start()], tmpdir, idx, args.path))
      ineqn = False
      tex = ''
    else:
      fout.write(line[start:m.start()])
      ineqn = True
    start = m.end()
  if ineqn:
    tex = tex + line[start:]
  else:
    fout.write(line[start:])

if args.input != None: fin.close()
if args.output != None: fout.close()
