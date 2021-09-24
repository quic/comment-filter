#  Copyright (c) 2017, Qualcomm Innovation Center, Inc. All rights reserved.
#  SPDX-License-Identifier: BSD-3-Clause

import re

class State:
    """Parser State"""
    def __init__(self, line='', multi_end_stack=None, in_literal=None):
        # The remaining input.
        self.line = line

        # A stack of end tokens for multi-line comments.  The token on the
        # top of the stack is the expected end token for the most nested
        # multi-line comment.
        self.multi_end_stack = multi_end_stack or []

        # If the parser is waiting on the end quote, in_literal will be
        # string the parser is waiting for.
        self.in_literal = in_literal

    def __eq__(self, x):
        # Return True if all members are equal.
        return self.line == x.line and self.multi_end_stack == x.multi_end_stack \
            and self.in_literal == x.in_literal


def parse_file(lang, file_obj, code_only=False, keep_tokens=True):
    """
    Return a generator that yields a filtered line for
    each line in file_obj.

    Args:
      lang (dictionary):
        Syntax description for the language being parsed.
      file_obj (iterator<string>):
        An iterater that yields lines.
      code_only (bool, default: False):
        If False, each non-comment character is replaced with a space.
        If True, each comment character is replaced with a space.
      keep_tokens (bool, default: True):
        If False, comment tokens are filtered out.
        If True, comment tokens are preserved.

    Returns:
      iterator<string>
    """
    state = State()
    for line in file_obj:
        state.line = line
        line, state = parse_line(lang, state, code_only, keep_tokens)
        yield line


def parse_line(lang, state, code_only=False, keep_tokens=True):
    """
    Return the comments or code of state.line.

    The output string will be the same length as the input string.
    Filtered out characters are represented as spaces.

    Args:
      lang (Language):
        Syntax description for the language being parsed.
      state (State):
        Parser state.
      code_only (bool, default: False):
        If False, each non-comment character is replaced with a space.
        If True, each comment character is replaced with a space.
      keep_tokens (bool, default: True):
        If False, comment tokens are filtered out.
        If True, comment tokens are preserved.

    Returns:
      (string, State)
    """
    # If currently within a string literal or multi-line comment, first
    # complete parsing that declaration.  Store the result in 'rest_of_decl'.
    rest_of_decl = ''
    if state.in_literal:
        # Parsing a string literal.
        cnts, state = finish_string_literal(state.in_literal, state)
        if code_only:
            rest_of_decl = cnts
        else:
            rest_of_decl = clear_line(cnts)
    elif state.multi_end_stack:
        # If there is state, we assume it is because we have parsed
        # the start of a multiline comment, but haven't found the end.
        cmt, state = finish_multiline_comment(lang, state, keep_tokens)
        if code_only:
            rest_of_decl = clear_line(cmt)
        else:
            rest_of_decl = cmt

    if state.in_literal or state.multi_end_stack:
        return rest_of_decl, state

    decls, state = parse_declarations(lang, state, code_only, keep_tokens)
    return rest_of_decl + decls, state


def parse_declarations(lang, state, code_only=False, keep_tokens=True):
    """
    Return the comments or code of state.line.

    Unlike parse_line, this function assumes the parser is *not*
    in the context of a multi-line comment.

    Args:
      lang (Language):
        Syntax description for the language being parsed.
      state (State):
        Parser state.
      code_only (bool, default: False):
        If False, each non-comment character is replaced with a space.
        If True, each comment character is replaced with a space.
      keep_tokens (bool, default: True):
        If False, comment tokens are filtered out.
        If True, comment tokens are preserved.

    Returns:
      (string, State)
    """
    code, state = parse_code(lang, state)
    comment, state = parse_line_comment(lang, state, keep_tokens)
    comment2, state = parse_multiline_comment(lang, state, keep_tokens)

    if comment or comment2:
        line = state.line
        if not state.multi_end_stack:
            # Continue looking for declarations.
            line, state = parse_declarations(lang, state, code_only, keep_tokens)
        if code_only:
            line = code + clear_line(comment) + clear_line(comment2) + line
        else:
            line = clear_line(code) + comment + comment2 + line
        return line, state
    else:
        state.line = ''
        if code_only:
            return code, state
        else:
            return clear_line(code), state


def parse_code(lang, state):
    """
    Returns all characters up to the first comment.

    Args:
      lang (Language):
        Syntax description for the language being parsed.
      state (State):
        Parser state.

    Returns:
      (string, State)
    """
    code = ''
    while True:
        line = state.line
        multi_start_tokens = [start for start, end in lang.comment_bookends]
        tokens = multi_start_tokens + [
            lang.line_comment,
            lang.string_literal_start,
            lang.string_literal2_start]
        i = index_of_first_found(line, tokens)
        if i != -1:
            state.line = line[i:]
            code += line[:i]
            if line.startswith(lang.line_comment, i) or \
                    index_of_first_found(line, multi_start_tokens) == i:
                return code, state
            elif line.startswith(lang.string_literal_start, i):
                lit, state = parse_string_literal(
                    lang.string_literal_start, state)
                code += lit
                continue
            else:
                lit, state = parse_string_literal(
                    lang.string_literal2_start, state)
                code += lit
                continue
        else:
            state.line = ''
            return code + line, state


def parse_string_literal(quote, state):
    """
    Returns the string literal at the beginning of state.line,
    otherwise the empty string.

    Args:
      quote (string):
        The syntax for the start and end quote.
      state (State):
        Parser state.

    Returns:
      (string, State)
    """
    if state.line.startswith(quote):
        state.line = state.line[len(quote):]
        line, state = finish_string_literal(quote, state)
        return quote + line, state
    else:
        return '', state


def finish_string_literal(quote, state):
    cnts, state = parse_string_literal_contents(quote, state)
    if state.line.startswith(quote):
        state.line = state.line[len(quote):]
        state.in_literal = None
        return cnts + quote, state
    else:
        # No end-quote yet.
        state.in_literal = quote
        return cnts, state


def parse_string_literal_contents(quote, state):
    """
    Returns the string literal contents at the beginning of state.line.
    The end quote is not included.

    Args:
      quote (string):
        The syntax for the end quote.
      state (State):
        Parser state.

    Returns:
      (string, State)
    """
    contents = ''
    escaped_quote = '\\' + quote
    while True:
        i = index_of_first_found(state.line, [quote, escaped_quote])
        if i != -1:
            if state.line.startswith(quote, i):
                contents += state.line[:i]
                state.line = state.line[i:]
                return contents, state
            else:
                # Escaped quote.
                i += len(escaped_quote)
                contents += state.line[:i]
                state.line = state.line[i:]
                continue
        else:
            # No end-quote.  Chew up the whole line.
            contents += state.line
            state.line = ''
            return contents, state


def parse_line_comment(lang, state, keep_tokens=True):
    """
    Returns the single-line comment at the beginning of state.line,
    otherwise the empty string.

    Args:
      lang (Language):
        Syntax description for the language being parsed.
      state (State):
        Parser state
      keep_tokens (bool, default: True):
        If False, comment tokens are filtered out.
        If True, comment tokens are preserved.

    Returns:
      (string, State)
    """
    line = state.line
    line_comment = lang.line_comment
    if line.startswith(line_comment):
        state.line = ''
        i = len(line_comment)
        if not keep_tokens:
            line_comment = ' ' * i
        return line_comment + line[i:], state
    else:
        return '', state


def parse_multiline_comment(lang, state, keep_tokens=True):
    """
    Returns the multi-line comment at the beginning of state.line,
    otherwise the empty string.

    Args:
      lang (Language):
        Syntax description for the language being parsed.
      state (State):
        Parser state
      keep_tokens (bool, default: True):
        If False, comment tokens are filtered out.
        If True, comment tokens are preserved.

    Returns:
      (string, State)
    """
    line = state.line
    for multi_start, multi_end in lang.comment_bookends:
        if line.startswith(multi_start):
            state.multi_end_stack.append(multi_end)
            state.line = line[len(multi_start):]
            cnts, state = finish_multiline_comment(lang, state, keep_tokens)
            if not keep_tokens:
                multi_start = ' ' * len(multi_start)
            return multi_start + cnts, state
    return '', state


def finish_multiline_comment(lang, state, keep_tokens=True):
    """
    Returns the rest of a multi-line comment at the beginning of state.line.

    Args:
      lang (Language):
        Syntax description for the language being parsed.
      state (State):
        Parser state
      keep_tokens (bool, default: True):
        If False, comment tokens are filtered out.
        If True, comment tokens are preserved.

    Returns:
      (string, State)
    """
    cnts, state = parse_multiline_contents(lang, state)
    multi_end = state.multi_end_stack[-1]

    # Handle language supports nested comments.
    if lang.nested_comments:
        cmt, state = parse_multiline_comment(lang, state, keep_tokens)
    else:
        cmt = ''

    line = state.line
    if line:
        if line.startswith(multi_end):
            i = len(multi_end)
            state.multi_end_stack.pop()
            state.line = line[i:]
            if not keep_tokens:
                multi_end = ' ' * len(multi_end)
            return cnts + cmt + multi_end, state
        else:
            more_cnts, state = finish_multiline_comment(lang, state, keep_tokens)
            return cnts + cmt + more_cnts, state
    else:
        return cnts + cmt, state


def parse_multiline_contents(lang, state):
    """
    Returns the multi-line comment contents at the beginning of state.line.

    Args:
      lang (Language):
        Syntax description for the language being parsed.
      state (State):
        Parser state

    Returns:
      (string, State)
    """
    line = state.line
    tokens = [start for start, end in lang.comment_bookends]
    multi_end = state.multi_end_stack[-1]
    tokens.append(multi_end)

    if lang.nested_comments:
        i = index_of_first_found(line, tokens)
    else:
        try:
            i = line.index(multi_end)
        except ValueError:
            i = -1

    if i != -1:
        state.line = line[i:]
        return line[:i], state
    else:
        # Reached the end of line before the end of comment.
        state.line = ''
        return line, state


def index_of_first_found(s, xs):
    """
    Return the index of the first string from xs found in s.
    """
    regex = '|'.join(map(re.escape, xs))
    m = re.search(regex, s)
    if m:
        return m.start()
    else:
        return -1


def clear_line(line):
    """
    Return a string where each non-newline character is replaced with a space.
    """
    sep = get_linesep(line)
    if sep:
        return ' ' * (len(line) - len(sep)) + sep
    else:
        return ' ' * len(line)


def get_linesep(line):
    """
    Returns the line separator if it exists, otherwise the empty string."
    """
    n = len(line)
    if n >= 2 and line[-2:] == '\r\n':
        return '\r\n'
    elif n >= 1 and line[-1] == '\n':
        return '\n'
    else:
        return ''
