#!/bin/bash

# Copyright (C) 2010-2014  Xyne
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# (version 2) as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

dpi=300
page=1
outputfmt=png
background="rgb 1 1 1"
#keeptmpdir


function display_help() {
  cat <<HELP
ABOUT
  tex2png - convert (La)TeX to PNG images

USAGE
  tex2png [options] [-- <dvi2png args>]

  A (La)Tex string can be passed either as a command-line parameter or via
  STDIN. When manually entered via STDIN, use ctrl+d to terminate input.

OPTIONS
  -b <color spec>
    The background color to pass to dvipng's "--bg" option. It should be given
    in TeX color \special syntax, e.g. "rgb 0.2 0.2 0.2". "Transparent" and
    "transparent" are also accepted. See the dvipng help message for more
    details. Default: 'transparent'

  -c <string>
    The (La)TeX string.

  -d <path>
    The output directory. See below.

  -D <int>
    The dpi argument passed to "dvipng". Default is 100. Increase this to
    increase font size.

  -f
    Specify the full input document. By default, tex2png provides its own
    headers and wraps the input in document tags. This option enables the user
    to provide a full (La)TeX document with custom headers.

  -i
    Inline mode. This will include the height and depth in the output, which can
    be used for vertical alignment in web pages, e.g. This should only be used
    when the tex contains mathematics.

  -h
    Display this help message.

  -o <path>
    The image path. See below.

  -p <int>
    Page number to render. Default is 1.

  -t <path>
    The temporary working directory. A random directory is created with "mktemp"
    by default.

  -T
    Crop whitespace around the content (dvipng -T tight).


OUTPUT
  If the image path is set then it is the full path to the image. If it is not
  set then the image name will be the sha256 digest of the (La)Tex input string
  with the ".png" extension. If the output directory has been set then the image
  will be saved there, otherwise it will be saved in the current directory.

DIV2PNG ARGUMENTS
  All arguments following "--" will be passed directly to dvi2png. See the
  dvi2png man page for details.


HELP

  exit
}

while getopts "b:c:d:D:fhio:p:s:St:T" flag; do
  case "$flag" in
    b) background="$OPTARG" ;;
    c) content="$OPTARG" ;;
    d) outputdir="${OPTARG/%\/}" ;;
    D) dpi="$OPTARG" ;;
    f) full="true" ;;
    h) display_help ;;
    i) _inline="true" ;;
    o) imgpath="$OPTARG" ;;
    p) page="$OPTARG" ;;
    s)
      echo 'warning: the -s option is deprecated. Use -D instead.' >&2
      # Divide by 14 because the old size default was 1400 which corresponds to
      # 100 DPI.
      dpi=$(($OPTARG / 14))
    ;;
    t) tmpdir="$OPTARG" ;;
    T) tight="true" ;;
  esac
done

shift $((OPTIND - 1))
dvipng_opts=("$@")


[[ -z $background ]] && background="transparent"
[[ -z $content ]] && { content="$(< /dev/stdin)" || exit 1; }
[[ -z $outputdir ]] && outputdir="$PWD"
[[ -z $imgpath ]] && imgpath="$outputdir/$(echo "full=${full};_inline=${_inline};page=${page};dpi=${dpi};tight=${tight};content=${content}" | shasum | cut -d' ' -f1).png"
if [[ -z $tmpdir ]]; then
  tmpdir=$(mktemp -d /tmp/tex2png_XXXXXX) || exit 1
else
  keeptmpdir="yes"
  mkdir -p "$tmpdir" || exit 1
fi

# If it's not a full document, create one.
if [[ -z $full ]]; then
  # This is just a workaround to handle inline tex outside of textmath.
  if [[ $_inline == 'true' ]]; then
     _preview="\usepackage[active,displaymath,textmath,sections,graphics,floats]{preview}"
#      content="\$\mbox{$content}\$"
  fi
  echo '\documentclass{article}' > "$tmpdir/content.tex"
  if [ "$tight" == "true" ]; then
    echo '\usepackage[paperwidth=\maxdimen,paperheight=\maxdimen]{geometry}' >> "$tmpdir/content.tex"
  fi
  cat >> "$tmpdir/content.tex" <<TEX
\pagestyle{empty}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{amssymb}
\usepackage{amsmath}
${_preview}
\begin{document}
\begin{samepage}
$content
\end{samepage}
\end{document}
TEX
else
  cat >"$tmpdir/content.tex" <<TEX
$content
TEX
fi

LC_ALL=C latex -halt-on-error -output-directory="$tmpdir" "$tmpdir/content.tex" >/dev/null  || exit 1
while [[ ! -e $tmpdir/content.dvi ]] || [[ ! -s $tmpdir/content.dvi ]]; do
  if [[ -e $tmpdir/content.log ]] \
  && [[ $(tail -n1 "$tmpdir/content.log") == 'No pages of output.' ]]
  then
    echo 'error: No pages of output.' >&2
    exit 1
  fi
  sleep 0.1
done
[[ -s $tmpdir/content.dvi ]] || exit 1
[[ $tight == "true" ]] && dvipng_opts+=(-T tight)
if [[ ${imgpath%/*} != $imgpath ]]
then
  mkdir -p "${imgpath%/*}"
fi
dvipng -q -D "$dpi" -p "$page" --height --depth "${dvipng_opts[@]}" -bg "$background" --png -z 9 -o "$imgpath" "$tmpdir/content.dvi" | grep -o 'depth=-\{0,1\}[0-9]\{1,\} height=-\{0,1\}[0-9]\{1,\}'  || exit 1
echo "file=$imgpath"
if [[ -z $keeptmpdir ]]; then
  rm -r "$tmpdir"
fi
