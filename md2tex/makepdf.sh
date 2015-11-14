#!/bin/bash
rm -rf ./dissertation
git clone https://git.gitbook.com/richarddzh/dissertation.git
cd dissertation
cp ../*.py .
../convert.sh
xelatex SUMMARY.tex
bibtex SUMMARY
xelatex SUMMARY.tex
xelatex SUMMARY.tex

