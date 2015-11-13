#!/bin/bash
for f in *.md
do
  fn=`basename $f .md`
  python md2tex.py -o "$fn.tex" "$f"
done
