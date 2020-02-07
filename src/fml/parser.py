from collections import namedtuple


Token = namedtuple('Token', ['kind', 'value', 'chars'])


class Lexer:
    r"""
    >>> L = Lexer('ayy\n "lmao"')
    >>> next(L)
    Token(kind='unquoted', value='ayy', chars='ayy')
    >>> next(L)
    Token(kind='newline', value='\n', chars='\n')
    >>> next(L)
    Token(kind='space', value=' ', chars=' ')
    >>> next(L)
    Token(kind='quoted', value='lmao', chars='"lmao"')
    >>> next(L)
    Traceback (most recent call last):
      ...
    StopIteration

    >>> for token in Lexer(r'"\"" "\\" "\x20"'): print(token)
    Token(kind='quoted', value='"', chars='"\\""')
    Token(kind='space', value=' ', chars=' ')
    Token(kind='quoted', value='\\', chars='"\\\\"')
    Token(kind='space', value=' ', chars=' ')
    Token(kind='quoted', value=' ', chars='"\\x20"')

    >>> list(Lexer(""))
    []
    >>> list(Lexer(" "))
    [Token(kind='space', value=' ', chars=' ')]
    """
    state = None

    def __init__(self, stream):
        # Don't touch this directly: use take/discard/accept
        self._stream = iter(stream)
        self.next = next(self._stream, None)
        self.position = 1
        self.line = 1
        self.column = 0

        self.prev = None
        self.kind = None
        self.value = []
        self.chars = []

    def token(self):
        return Token(
            kind=self.kind,
            value=''.join(self.value),
            chars=''.join(self.chars),
        )

    def take(self):
        char = self.next
        if char is None:
            raise StopIteration
        self.chars.append(char)
        self.next = next(self._stream, None)
        self.position += 1
        if char == '\n':
            self.line += 1
            self.column = 0
        else:
            self.column += 1
        return char

    def discard(self):
        self.take()

    def accept(self):
        self.value.append(self.take())

    def reject(self, msg):
        raise Exception(msg)

    def insert(self, char):
        self.value.append(char)

    def __iter__(self):
        return self

    def __next__(self):
        self.kind = None
        self.value.clear()
        self.chars.clear()

        if self.next is None:
            raise StopIteration
        elif self.next == '\n':
            self.kind = 'newline'
        elif self.next in ' \t':
            self.kind = 'space'
        elif self.next == '"':
            self.kind = 'quoted'
        else:
            self.kind = 'unquoted'

        getattr(self, self.kind)()

        self.prev = token = self.token()
        return token

    def newline(self):
        assert self.next == '\n'
        self.accept()

    def space(self):
        assert self.next in set(' \t')
        while self.next in set(' \t'):
            self.accept()

    def quoted(self):
        assert self.next == '"'
        self.discard()  # Don't include the opening quote.
        while True:
            if self.next is None:
                self.reject(
                    f"unterminated quoted text: {''.join(self.chars)!r}")
            elif self.next == '"':
                self.discard()  # Don't include the closing quote.
                break
            elif self.next == '\\':
                self.quoted_escaped()
            else:
                self.accept()

    simple_escapes = {
        '\\': '\\',
        '"': '"',
        'a': chr(7),
        'b': chr(8),
        'f': chr(12),
        'n': chr(10),
        'r': chr(13),
        't': chr(9),
        'v': chr(11),
    }

    def quoted_escaped(self):
        assert self.next == '\\'
        self.discard()  # Don't include the escape character.
        char = self.take()
        if char in self.simple_escapes:
            self.insert(self.simple_escapes[char])
        elif char == 'o':
            self.number(base=8, digits=2)
        elif char == 'x':
            self.number(base=16, digits=2)
        else:
            print(f"warning: {char!r} is not an escape sequence")
            self.accept()

    valid_digits = {
        2: '01',
        8: '01234567',
        10: '0123456789',
        16: '0123456789abcdefABCDEF'
    }

    def number(self, base, digits):
        chars = []
        for _ in range(digits):
            char = self.take()
            if char not in self.valid_digits[base]:
                self.reject(f"{char!r} is not a valid base-{base} digit")
            chars.append(char)
        number = ''.join(chars)
        value = int(number, base=base)
        char = chr(value)
        self.insert(char)

    def unquoted(self):
        assert self.next not in set('\n \t"')
        while True:
            if self.next is None:
                break
            elif self.next == '"':
                self.reject("quotes must be preceded by whitespace")
            elif self.next in '\n \t':
                break
            else:
                self.accept()
