#  Copyright (c) 2017, Qualcomm Innovation Center, Inc. All rights reserved.
#  SPDX-License-Identifier: BSD-3-Clause

from . import rfc
from . import language
from functools import reduce, wraps
from sys import getrecursionlimit, setrecursionlimit

try:
    from cStringIO import StringIO
except:
    from io import StringIO


# Same as rfc.parse_line(), but ensure it always returns a string with the
# same length as the input string.
def safe_parse_line(lang, state, **kwargs):
    old_line = state.line
    new_line, new_state = rfc.parse_line(lang, state, **kwargs)
    assert len(new_line) == len(old_line)
    return new_line, new_state


def make_state(line='', multi_end_stack=None, in_literal=None):
    return rfc.State(line, multi_end_stack, in_literal)


def test_state():
    """
    Verify constructor doesn't return a global default value.
    """
    rfc.State().multi_end_stack.append('doh!')
    assert(len(rfc.State().multi_end_stack) == 0)


def c_line(s):
    """
    Given a string, return only the C comments, and in the column same position.
    """
    line, state = safe_parse_line(language.c, make_state(s))
    assert state.multi_end_stack == []
    return line


def c_code(s):
    """
    Given a string, return only the C code, and in the column same position.
    """
    line, state = safe_parse_line(language.c, make_state(s), code_only=True)
    assert state.multi_end_stack == []
    return line


def py_line(s):
    """
    Given a string, return only the Python comments, and in the column same position.
    """
    line, state = safe_parse_line(language.python, make_state(s))
    assert state.multi_end_stack == []
    return line


def java_line(s):
    """
    Given a string, return only the Java comments, and in the column same position.
    Unlike c_line, java_line supports nested comments.
    """
    line, state = safe_parse_line(language.java, make_state(s))
    assert state.multi_end_stack == []
    return line


def parse_code(lang, line):
    return rfc.parse_code(lang, make_state(line))

def test_parse_code():
    c = language.c
    assert parse_code(c, '') == ('', make_state(''))
    assert parse_code(c, '\n') == ('\n', make_state(''))
    assert parse_code(c, 'foo // bar') == ('foo ', make_state('// bar'))
    assert parse_code(c, 'foo /* bar') == ('foo ', make_state('/* bar'))  # Ensure '*' is escapted.
    assert parse_code(c, '/**/ foo') == ('', make_state('/**/ foo'))  # Only return code /before/ comments.

    # Multi-line Python strings are treated as comments.
    assert parse_code(language.python, '""" bar """') == ('', make_state('""" bar """'))


def line_comment(lang, line, keep_tokens=True):
    cmt, state = rfc.parse_line_comment(lang, make_state(line), keep_tokens)
    return (cmt, state.line)


def test_parse_line_comment():
    c = language.c
    assert line_comment(c, '') == ('', '')
    assert line_comment(c, '\n') == ('', '\n')
    assert line_comment(c, '//\n') == ('//\n', '')
    assert line_comment(c, '//\n', False) == ('  \n', '')


def test_index_of_first_found():
    assert rfc.index_of_first_found('', []) == 0  # Nothing to find.
    assert rfc.index_of_first_found('', ['a']) == -1  # Nothing found.
    assert rfc.index_of_first_found('ab', ['b']) == 1  # 'b' found.
    assert rfc.index_of_first_found('abc', ['b', 'c']) == 1  # 'b' found first.
    assert rfc.index_of_first_found('acb', ['b', 'c']) == 1  # 'c' found first.


def test_clear_line():
    assert rfc.clear_line('') == ''
    assert rfc.clear_line('abc') == '   '
    assert rfc.clear_line('abc\n') == '   \n'  # Preserve newline.
    assert rfc.clear_line('abc\r\n') == '   \r\n'  # Preserve multibyte newline.


def test_get_linesep():
    assert rfc.get_linesep('') == ''
    assert rfc.get_linesep('foo\n') == '\n'
    assert rfc.get_linesep('foo\r\n') == '\r\n'
    assert rfc.get_linesep('foo\r\nbar\n') == '\n'


def multiline_comment(lang, line, keep_tokens=True):
    return rfc.parse_multiline_comment(lang, make_state(line), keep_tokens)


def test_parse_multiline_comment():
    c = language.c
    assert multiline_comment(c, '/**/\n') == ('/**/', make_state('\n'))
    assert multiline_comment(c, '/**/\n', False) == ('    ', make_state('\n'))


def declarations(lang, line, keep_tokens=True):
    return rfc.parse_declarations(lang, make_state(line), keep_tokens=keep_tokens)


def test_parse_declarations():
    c = language.c
    assert declarations(c, '\n') == ('\n', make_state())
    assert declarations(c, '/**/\n') == ('/**/\n', make_state())


def test_parse_line():
    assert c_line('') == ''
    assert c_line('no comments') == '           '
    assert c_line('/**/') == '/**/'
    assert c_line('/* a */') == '/* a */'
    assert c_line('// a') == '// a'
    assert py_line('""" a """') == '""" a """'
    assert py_line("''' a '''") == "''' a '''"

    # Preserve newline
    assert c_line('/* a */\n') == '/* a */\n'

    # Ensure column position is not modified.
    assert c_line('abc /* a */') == '    /* a */'
    assert c_line('abc // a') == '    // a'

    # Test comments in comments
    assert c_line('// /*abc*/') == '// /*abc*/'
    assert c_line('/* a */ // a') == '/* a */ // a'
    assert java_line('/* /**/ */') == '/* /**/ */'
    assert java_line('/*/**/*/') == '/*/**/*/'
    assert c_line('/*/**/*/') == '/*/**/  '
    assert c_line('/* // */') == '/* // */'
    assert py_line('"""# a"""') == '"""# a"""'

    # Test strings with strings
    assert c_line('"\\\"foo\\\""') == '         '
    assert c_line('"foo') == '    '

    # Test string literals with comments
    assert c_line('"/*"') == '    '
    assert c_line("'/*'") == '    '

    # Test c_code
    assert c_code('') == ''
    assert c_code('no comments') == 'no comments'
    assert c_code('/**/') == '    '
    assert c_code('/* a */\n') == '       \n'
    assert c_code('/* a */ abc') == '        abc'
    assert c_code('abc /**/') == 'abc     '


def string_literal(quote, line):
    lit, state = rfc.parse_string_literal(quote, make_state(line))
    return (lit, state.line)


def test_parse_string_literal():
    assert string_literal('"', 'abc') == ('', 'abc')
    assert string_literal('"', '"a"') == ('"a"', '')
    assert string_literal("'", "'a'") == ("'a'", '')
    assert string_literal("'", "'a'b") == ("'a'", 'b')

    # String without an end quote.
    assert string_literal('"', '"a') == ('"a', '')


def parse_line(lang, line, multi_end_stack=None, code_only=False):
    return safe_parse_line(lang, make_state(line, multi_end_stack), code_only=code_only)


def test_incomplete_multiline():
    c = language.c
    assert parse_line(c, '/* a\n') == ('/* a\n', make_state('', ['*/']))


def test_incomplete_string_literal():
    c = language.c
    assert parse_line(c, '" a \\\n', code_only=True) == ('" a \\\n', make_state('', None, '"'))


def test_previous_state_maintained():
    c = language.c
    assert parse_line(c, '', ['foo']) == ('', make_state('', ['foo']))
    assert parse_line(c, '/**/', ['foo']) == ('/**/', make_state('', ['foo']))
    assert parse_line(c, '/*', ['foo']) == ('/*', make_state('', ['foo']))
    j = language.java
    assert parse_line(j, '/*', ['foo']) == ('/*', make_state('', ['foo', '*/']))


def test_code_of_resumed_multiline_comment():
    c = language.c
    assert parse_line(c, 'a', ['*/'], True) == (' ', make_state('', ['*/']))
    assert parse_line(c, 'a */', ['*/'], True) == ('    ', make_state('', []))


def parse_lit_line(lang, line, code_only=False):
    return safe_parse_line(lang, make_state(line, None, lang.string_literal_start), code_only=code_only)


def test_previous_state_maintained_literal():
    c = language.c
    assert parse_lit_line(c, '') == ('', make_state('', in_literal='"'))
    assert parse_lit_line(c, '"') == (' ', make_state(''))


def test_code_of_resumed_multiline_literal():
    c = language.c
    assert parse_lit_line(c, '', True) == ('', make_state('', in_literal='"'))
    assert parse_lit_line(c, '"', True) == ('"', make_state(''))


def c_comments(s, keep_tokens=True):
    return list(rfc.parse_file(language.c, StringIO(s), keep_tokens=keep_tokens))


def test_parse_file():
    assert c_comments('/* hello */ world\n') == ['/* hello */      \n']
    assert c_comments('/* hello */ world\n', False) == ['   hello         \n']


def test_parse_comments_via_reduce():
    def f(st, x):
        st.line = x
        _, st = safe_parse_line(language.c, st)
        return st

    assert reduce(f, ['/*a', 'b*/'], make_state()) == make_state()
    assert reduce(f, ['/*a', 'b'], make_state()) == make_state('', ['*/'])
