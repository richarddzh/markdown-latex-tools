#!/bin/bash
# convert all markdown files in the current dir
pybin=python3
command -v $pybin > /dev/null 2>&1 || pybin=python
for f in *.md
do
  fn=`basename $f .md`
  $pybin md2tex.py -o "$fn.tex" "$f"
done

