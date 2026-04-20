from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class _StringToken:
    value: str


class SExpressionParseError(ValueError):
    """Raised when an S-expression cannot be parsed."""


def _tokenize(source: str) -> list[str | _StringToken]:
    tokens: list[str | _StringToken] = []
    index = 0

    while index < len(source):
        character = source[index]

        if character.isspace():
            index += 1
            continue

        if character in ("(", ")"):
            tokens.append(character)
            index += 1
            continue

        if character == '"':
            index += 1
            buffer: list[str] = []

            while index < len(source):
                current = source[index]
                if current == "\\":
                    index += 1
                    if index >= len(source):
                        raise SExpressionParseError("unterminated string escape")
                    buffer.append(source[index])
                elif current == '"':
                    index += 1
                    break
                else:
                    buffer.append(current)
                index += 1
            else:
                raise SExpressionParseError("unterminated string literal")

            tokens.append(_StringToken("".join(buffer)))
            continue

        start = index
        while index < len(source) and not source[index].isspace() and source[index] not in ("(", ")"):
            index += 1
        tokens.append(source[start:index])

    return tokens


def _parse_expression(tokens: list[str | _StringToken], index: int) -> tuple[object, int]:
    if index >= len(tokens):
        raise SExpressionParseError("unexpected end of input")

    token = tokens[index]
    if token == "(":
        items: list[object] = []
        index += 1

        while index < len(tokens) and tokens[index] != ")":
            item, index = _parse_expression(tokens, index)
            items.append(item)

        if index >= len(tokens) or tokens[index] != ")":
            raise SExpressionParseError("missing closing parenthesis")

        return items, index + 1

    if token == ")":
        raise SExpressionParseError("unexpected closing parenthesis")

    if isinstance(token, _StringToken):
        return token.value, index + 1

    return token, index + 1


def parse_sexp(source: str) -> object:
    tokens = _tokenize(source)
    parsed, next_index = _parse_expression(tokens, 0)
    if next_index != len(tokens):
        raise SExpressionParseError("unexpected trailing tokens")
    return parsed


def plist_to_dict(value: object) -> dict[str, object]:
    if not isinstance(value, list):
        raise SExpressionParseError("expected a property list")

    if len(value) % 2 != 0:
        raise SExpressionParseError("property list contains an uneven number of items")

    payload: dict[str, object] = {}
    for position in range(0, len(value), 2):
        key = value[position]
        if not isinstance(key, str) or not key.startswith(":"):
            raise SExpressionParseError("property list key must be a keyword symbol")
        payload[key[1:].lower()] = value[position + 1]

    return payload
