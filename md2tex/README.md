md2tex
======

## Usage

    md2tex.py [-h] [-c ENCODING] [-o OUTPUT] [file [file ...]]

convert markdown to latex.

positional arguments:
 *  `file`         input files

optional arguments:
 *  `-h`, `--help`   show this help message and exit
 *  `-c ENCODING`  file encoding
 *  `-o OUTPUT`    output file

## Description

A python tool to convert markdown to latex.
Require Python 3.
I write all strings without u-decoration (Python 2).
The code does not work in Python 2.

 - md2tex.py: markdown to latex converter.
 - markdown.py: simple markdown parser.
 - convert.sh: bash script to convert markdown within current dir.
 - makepdf.sh: bash script pull dissertation from git repository and build pdf with xelatex.

## Supported markdown format

 - title: `#` prefix-styled title (from chapter to section, subsection, etc.).
 - image: `![caption](filename)` only support local files.
 - comment: html comment is supported and used for embedding latex.
 - table: `|cell|cell|` styled table.
 - math: only allow `$$` wrapped equations. 
          Inline equations cannot cross multiple lines.
          Block equations must have `$$` in a single line.
 - list: numbered list and `*+-` list are both supported. Nested list is OK.
 - href: only `*[description](filename)` styled table-of-contents items are supported.
          This will generate `input` command in latex.

## Special extension for latex

 - inline latex: start with a single line `<!-- latex` and end with a single line `-->`.
 - attributes: set attributes used for latex `<!-- set name1="value1" name2="value2" -->`.
   - `width`: for image, e.g. `width="0.5"` will generate `0.5\linewidth`. default: 0.5.
   - `label`: for image, table and equation. default: nolabel.
   - `float`: for image and table. default: ht.
   - `caption`: for table. default: empty string.
   - `columns`: for table, tabular columns specification. default: c.
 - references: refer to citation, label.
   - `[ref@item1,item2]`: generate `\ref{item1,item2}`.
   - `[cite@item1,item2]`: generate `\cite{item1,item2}`.
        
