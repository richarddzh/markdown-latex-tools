#!/bin/bash
#rm -rf ./dissertation
#git clone https://git.gitbook.com/richarddzh/dissertation.git
cd dissertation
git pull origin master
cp ../*.py .
rm *.tex *.out *.bbl *.blg *.log *.pdf *.toc *.aux
../convert.sh
xelatex SUMMARY.tex
bibtex SUMMARY
xelatex SUMMARY.tex
xelatex SUMMARY.tex
xelatex SUMMARY.tex

