<!-- latex
\documentclass{book}
\usepackage{graphicx}
\begin{document}
-->
# title 1
## title 2
### title has $$\alpha$$

<!-- set float="ht" width="0.8" label="fig:1" -->
![caption has $](img.png)

<!-- set caption="表格1 has % and $$\beta$$" columns="cc" float="ht" label="tab:1" -->
|h1|h2|
|--|--|
|$$\sum_i i+1$$|p\\p|
|pp|pp|
 1. item one
 *  item two
   - sub item
   + add item $$\mathcal{X}=\delta(y^{-1})$$, $$c=1$$
     * sub sub item
 3. item three

<!-- set label="equ:1" -->
$$
x = \sqrt{y}
+ z
$$

<!-- set caption="title of listing" -->
```matlab
function a = f(x)
  a = x + 1
end
```

this is code too:
```
\usepackage{listings}
```

1. item
this is going on
2. item **something bold** [cite@dong1986,zheng2015], [ref@fig:1,fig:2], [ref@tab:1]

**bold things here** that is it

this is the end
* [chapter 1](chapter1.md)

<!-- latex
\end{document}
-->
