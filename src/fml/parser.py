from collections import namedtuple


Token = namedtuple('Token', ['kind', 'value', 'chars'])


class Lexer:
    state = None

    def __init__(self, stream):
        # Don't touch this directly: use take/discard/accept
        self._stream = iter(stream)
        self.next = next(self._stream, None)

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
        return char

    def discard(self):
        self.take()

    def accept(self):
        self.value.append(self.take())

    def reject(self, msg):
        raise Exception(msg)

    def insert(self, char):
        self.value.append(char)

    def __next__(self):
        self.kind = None
        self.value.clear()
        self.chars.clear()

        char = self.next
        if char is None:
            raise StopIteration
        elif char == '\n':
            self.kind = 'newline'
        elif char in ' \t':
            self.kind = 'space'
            # if self.kind is None or self.kind == 'newline':
            #     self.kind = 'indentation'
            # else:
            #     self.kind = 'space'
        elif char == '"':
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
        assert self.next in ' \t'
        while self.next in ' \t':
            self.accept()

    def quoted(self):
        assert self.next == '"'
        self.discard()  # Don't include the opening quote.
        while True:
            char = self.next
            if char is None:
                self.reject(
                    f"unterminated quoted text: {''.join(self.chars)!r}")
            elif char == '"':
                self.discard()  # Don't include the closing quote.
                break
            elif char == '\\':
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
            value = self.simple_escapes[char]
        elif char == 'o':
            code = self.take() + self.take()
            point = int(code, base=8)
            value = chr(point)
        elif char == 'x':
            code = self.take() + self.take()
            point = int(code, base=16)
            value = chr(point)
        else:
            print(f"warning: {char!r} is not an escape sequence")
            value = char
        self.insert(value)

    def unquoted(self):
        assert self.next not in '\n \t"'
        while True:
            char = self.next
            if char is None:
                break
            elif char == '"':
                self.reject("quotes must be preceded by whitespace")
            elif char in '\n \t':
                break
            else:
                self.accept()
