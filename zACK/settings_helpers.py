from typing import Sequence


def one(*bools: Sequence[bool]) -> bool:
    """Check if exactly one element of a sequence is True."""
    found = False
    for _bool in bools:
        assert isinstance(_bool, bool)
        if _bool is not True:
            continue
        if found:
            return False
        found = True
    return found
