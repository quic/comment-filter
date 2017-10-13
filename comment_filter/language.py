class Lang:
    def __init__(self, line_comment, comment_bookends, nested_comments):
        self.line_comment = line_comment
        self.comment_bookends = comment_bookends
        self.nested_comments = nested_comments
        self.string_literal_start = '"'
        self.string_literal2_start = "'"

c = Lang(
    line_comment='//',
    comment_bookends=[('/*', '*/'), (';;', ';;')],
    nested_comments=False)

haskell = Lang(
    line_comment='--',
    comment_bookends=[('{-', '-}')],
    nested_comments=True)

python = Lang(
    line_comment='#',
    comment_bookends=[('"""', '"""'), ("'''", "'''")],
    nested_comments=False)

ruby = Lang(
    line_comment='#',
    comment_bookends=[("=begin", "=end")],
    nested_comments=False)

lua = Lang(
    line_comment='--',
    comment_bookends=[("--[[", "--]]")],
    nested_comments=False)

perl = Lang(
    line_comment='#',
    comment_bookends=[("=pod", "=cut")],
    nested_comments=False)

java = Lang(
    line_comment='//',
    comment_bookends=[('/*', '*/')],
    nested_comments=True)

go = c

extension_to_lang_map = {
    '.c': c,
    '.cc': c,
    '.cxx': c,
    '.cpp': c,
    '.h': c,
    '.S': c,
    '.java': java,
    '.go': go,
    '.hs': haskell,
    '.py': python,
    '.rb': ruby,
    '.lua': lua,
    '.pl': perl,
}
