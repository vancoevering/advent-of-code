from typing import Iterable
from tokenizer import MappingTokenizer
from pathlib import Path

THIS_DIR = Path(__file__).parent
INPUT_FILE_PATH = THIS_DIR / "input.txt"


NUMBER_WORDS_TO_NUMERALS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}
NUMERALS = list(NUMBER_WORDS_TO_NUMERALS.values())


def main():
    """Solve the puzzle: https://adventofcode.com/2023/day/1"""
    input = get_input_lines()
    solve_part_one(input)
    solve_part_two(input)


def get_input_lines():
    """Return input file lines as list of strings."""
    with INPUT_FILE_PATH.open("rt") as f:
        return f.read().splitlines()


def solve_part_one(input: Iterable[str]):
    tokenizer = MappingTokenizer({value: value for value in NUMERALS})
    calibration_numbers = get_calibration_numbers(input, tokenizer)
    calibration_sum = sum(calibration_numbers)
    print("Part one solution:", calibration_sum)


def solve_part_two(input: Iterable[str]):
    tokenizer = MappingTokenizer.from_singly_mapped_tokens(NUMBER_WORDS_TO_NUMERALS)
    input = [line.lower() for line in input]
    calibration_numbers = get_calibration_numbers(input, tokenizer)
    calibration_sum = sum(calibration_numbers)
    print("Part two solution:", calibration_sum)


def get_calibration_numbers(input: Iterable[str], tokenizer: MappingTokenizer):
    return [
        int(
            tokenizer.get_first_token(line).value + tokenizer.get_last_token(line).value
        )
        for line in input
    ]


if __name__ == "__main__":
    main()
