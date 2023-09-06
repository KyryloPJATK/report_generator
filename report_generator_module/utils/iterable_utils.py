from typing import List


def find_occurrences(source: str, ch: str) -> List[int]:
    """
        Finds all occurrences of provided character in source

        :param source: source string to parse
        :param ch: character to seek

        :returns List of matched indexes
    """
    return [i for i, letter in enumerate(source) if letter == ch]


def replace(source, target, from_idx, to_idx=None) -> str:
    if not to_idx:
        to_idx = from_idx
    return source[:from_idx] + target + source[to_idx + 1:]
