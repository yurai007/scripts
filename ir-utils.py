#!/usr/bin/python3

from string import Template
from collections import deque
import sys
import re

# simple heuristic without real parsing, may produce false positives
def self_referenced_or_badref(line):
    splitted = re.split(" |, ", line.lstrip())
    if "<badref>" in splitted:
        return True
    eq = lambda word: word == "="
    identifier = lambda word: '%' in word
    filtered = [word for word in splitted if eq(word) or identifier(word)]
    if not filtered:
        return False
    first_id = [i for i, word in enumerate(filtered) if identifier(word)]
    if not first_id:
        return False
    idx = first_id[0]
    match filtered[idx:idx + 3]:
        case [left, op, right] if eq(op) and left == right:
            return True
        case _:
            return False

def main():
    if len(sys.argv) != 2:
        return
    filename = sys.argv[1]
    cin = open(filename, 'r')
    lines = deque([line.rstrip('\n') for line in cin])
    cin.close()
    while lines:
        line = lines.popleft()
        if self_referenced_or_badref(line):
            print(f"warning: detected ill-formed IR in '{line}'")

if __name__ == "__main__":
    main()
