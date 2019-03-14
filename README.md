Comment Filter
==============

[![CircleCI](https://circleci.com/gh/codeauroraforum/comment-filter.svg?style=svg)](https://circleci.com/gh/codeauroraforum/comment-filter)

A Python library and command-line utility that filters comments from a source
code file, replacing each non-comment character with a space.

When run from the the command-line, the `comment` utility will generate an
output file in which any comment text will remain at the same line and column
as the input file.

The Python library provides one function `parse_file()`, which streams the
input file and returns the filtered file contents via a generator that yields
one line at a time.

Both interfaces support an 'only code' option that inverts the functionality
such that comment text is replaced by spaces and the code text is preserved in
its original location.

There is also a 'no tokens' option which will preserve the comments, but
replace the comment tokens with spaces (in addition to the code text).


hello.c:

```c
/* multi-line
   comment */
// single-line comment

int main() {
  return 0;
}
```

Example of getting the comments in a C file:

```bash
$ comments hello.c
/* multi-line
   comment */
// single-line comment
```

When filtering for comments, any character that is not the start of a comment
is replaced with a space.

To get comments without the comment tokens:

```bash
$ comments --notokens hello.c
   multi-line
   comment
   single-line comment
```

Filter out the comments:

```bash
$ comments --onlycode hello.c




int main() {
  return 0;
}
```


Python library
--------------

Alternatively, one can use the provided Python library directly.  It provides
one function `parse_file()`, which streams the input file and returns
the filtered file via a generator.  The generator yields one line at a time.


Implementation Notes
--------------------

A challenging requirement is that the parser is only fed one line at a time.
This means that we cannot leverage most Python parsing libraries, including
PyParsing, PyPEG, or even the Haskell Parsec-inspired funcparserlib.  Instead,
we need stream parsing combinators, like those provided by Haskell's Conduit
or Iteratee.  But in Python, and for this small parser, implementing that
infrastructure seemed like overkill.  Unlike Haskell, Python cannot optimize
out the additional abstraction layer.  So this library implements streaming,
recursive-decent parsers by hand.  Lots of ugly noise in the code, but lots
and lots of unit tests to keep complexity under control.


Grammar
-------

```antlr
file                 : declaration* ;

declaration          : line_comment | multiline_comment | code ;

line_comment         : line_comment_start (~endl)* endl ;

multiline_comment    : multiline_comment_start multiline_contents multiline_comment_end ;
multiline_contents   : (multiline_char | multiline_comment)* ;
multiline_char       : ~(multiline_comment_start | multiline_comment_end) ;

code                 : (string_literal | code_char)* ;
code_char            : ~(string_literal_start | line_comment_start | multiline_comment_start) ;

string_literal       : string_literal_start string_literal_char* string_literal_end ;
string_literal_char  : escape_char (string_literal_start | string_literal_end)
                     | ~(escape_char | string_literal_end) ;
```

The syntax for the following tokens are provided by the `language` module:

  * line_comment_start
  * multiline_comment_start
  * multiline_comment_end
  * string_literal_start
  * string_literal_end
  * escape_char


Recognized Languages
--------------------

  * C
  * C++
  * Go
  * Haskell
  * Java
  * Lua
  * Python
  * Perl
  * Ruby


Developing
----------

This assumes the following are installed and in your system path:

   * Python 2.7.x OR Python 3.4.x
   * tox

To build and test, run `tox`.

```bash
$ tox
```

To remove all files not registered with git.

```bash
$ git clean -Xdf
```
