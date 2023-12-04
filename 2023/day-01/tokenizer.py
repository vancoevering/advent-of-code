from collections import namedtuple
from dataclasses import dataclass
from enum import Enum, auto


Tokens = dict[str, str]
TokenResult = namedtuple("TokenResult", ["token", "value"])
ShiftEnd = namedtuple("ShiftEnd", ["shift", "end"])


class TokenizerDirection(Enum):
    FORWARD = auto()
    BACKWARD = auto()


@dataclass
class TrackedToken:
    token: str
    i: int

    def is_valid(self, c: str):
        return c == self.token[self.i]


class MappingTokenizer:
    def __init__(self, tokens: Tokens) -> None:
        self.tokens = tokens
        self.heads = self._get_heads(tokens)
        self.tails = self._get_tails(tokens)

    @classmethod
    def _get_heads(cls, tokens: Tokens):
        return cls._get_starters(tokens, TokenizerDirection.FORWARD)

    @classmethod
    def _get_tails(cls, tokens: Tokens):
        return cls._get_starters(tokens, TokenizerDirection.BACKWARD)

    @staticmethod
    def _get_starters(tokens: Tokens, direction: TokenizerDirection):
        starters: dict[str, list[str]] = {}
        for key in tokens:
            if len(key) <= 1:
                continue
            starter = key[0] if direction == TokenizerDirection.FORWARD else key[-1]
            if starter not in starters:
                starters[starter] = []
            starters[starter].append(key)
        return starters

    @classmethod
    def from_singly_mapped_tokens(cls, tokens: Tokens):
        """
        Create this class from a token map where each
        value is also a valid token mapped to itself.
        """
        new_tokens = {key: value for key, value in tokens.items()}
        for _, value in tokens.items():
            new_tokens[value] = value
        return cls(new_tokens)

    def get_first_token(self, s: str):
        return self._get_token(s, TokenizerDirection.FORWARD)

    def get_last_token(self, s: str):
        return self._get_token(s, TokenizerDirection.BACKWARD)

    def _get_token(self, s: str, direction: TokenizerDirection):
        tracked_tokens: list[TrackedToken] = []
        director, starters, i = self._get_token_helper(direction)
        for c in director(s):
            # Is this char a single-length token
            if c in self.tokens:
                return TokenResult(c, self.tokens[c])

            # Does this char continue our tracked token patterns
            tracked_tokens, result = self._update_tracked_tokens(
                c, tracked_tokens, direction
            )
            if result:
                return TokenResult(result, self.tokens[result])

            # Could this char be the start of a multi-length token
            if c in starters:
                for token in starters[c]:
                    tracked_tokens.append(TrackedToken(token=token, i=i(token)))
        raise ValueError("No token found!")

    def _get_token_helper(self, direction: TokenizerDirection):
        if direction == TokenizerDirection.FORWARD:
            return (str, self.heads, lambda x: 1)
        else:
            return (reversed, self.tails, lambda x: len(x) - 2)

    def _update_tracked_tokens(
        self, c: str, tracked: list[TrackedToken], direction: TokenizerDirection
    ):
        new_tracked = []
        shift, end = self._get_update_shift_end(direction)
        for token in tracked:
            if token.is_valid(c):
                token.i = shift(token.i)
                if token.i == end(token.token):
                    return (tracked, token.token)
                new_tracked.append(token)
        return (new_tracked, None)

    @staticmethod
    def _get_update_shift_end(direction: TokenizerDirection):
        if direction == TokenizerDirection.FORWARD:
            return ShiftEnd(shift=lambda x: x + 1, end=lambda x: len(x))
        else:
            return ShiftEnd(shift=lambda x: x - 1, end=lambda x: -1)
