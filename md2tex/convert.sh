#!/bin/bash
# convert all markdown files in the current dir
for f in *.md
do
  fn=`basename $f .md`
  python md2tex.py -o "$fn.tex" "$f"
done

