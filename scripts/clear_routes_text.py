from __future__ import annotations

import argparse
from pathlib import Path


def find_block_end(text: str, start: int) -> int:
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError("unterminated block")


def remove_blocks(text: str, starts: tuple[str, ...]) -> tuple[str, int]:
    output: list[str] = []
    cursor = 0
    removed = 0
    while cursor < len(text):
        matches = [(text.find(start, cursor), start) for start in starts]
        matches = [(position, start) for position, start in matches if position != -1]
        if not matches:
            output.append(text[cursor:])
            break
        start, marker = min(matches)
        output.append(text[cursor:start])
        end = find_block_end(text, start)
        cursor = end
        while cursor < len(text) and text[cursor] in " \t\r\n":
            cursor += 1
        output.append("\n")
        removed += 1
    return "".join(output), removed


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove PCB segment/via routing blocks without pcbnew SWIG iteration.")
    parser.add_argument("board", type=Path)
    args = parser.parse_args()

    text = args.board.read_text(encoding="utf-8")
    text, removed = remove_blocks(text, ("(segment", "(via"))
    args.board.write_text(text, encoding="utf-8", newline="")
    print(f"Removed {removed} route block(s)")


if __name__ == "__main__":
    main()